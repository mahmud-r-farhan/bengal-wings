# ==============================================================================
# 🦅 BENGAL WINGS :: GCS CORE — TELEMETRY STREAM SERVER (Zero-Dependency)
# ------------------------------------------------------------------------------
# Implements the Phase 1 roadmap item "Telemetry Stream and Ground Control
# Station (GCS) Core" as a fully runnable reference:
#
#   * ThreadingHTTPServer serving the tactical dashboard from gcs/web/
#   * WebSocket endpoint  /ws/telemetry   (10 Hz JSON telemetry push)
#   * HTTP fallback       /api/telemetry  (snapshot polling when WS blocked)
#   * JSON command        /api/command    (POST arm|takeoff|hold|rtl|land|
#                                          goto|x,y|jam|speed|reset)
#
# The WebSocket layer is implemented directly on the RFC 6455 framing rules
# using only the Python standard library — no pip installs on the Jetson,
# the ground laptop, or CI.
#
# Run from the repo root:   python3 -m gcs --port 8090
# ==============================================================================
"""Bengal Wings GCS telemetry server (stdlib only)."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import socket
import struct
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple

from .sim import BengalWingsSim

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
MAX_FRAME = 1 << 16  # 64 KiB — commands are tiny; anything bigger is refused


# =============================================================================
# RFC 6455 frame codec (importable + unit-tested in tests/test_gcs.py)
# =============================================================================
def ws_encode(payload, opcode: int = 0x1, mask: bool = False) -> bytes:
    """Encode a single (non-fragmented) WS frame, server-to-client style.
    `payload` may be str (UTF-8 encoded) or raw bytes."""
    data = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    head = bytearray([0x80 | opcode])
    n = len(data)
    if n < 126:
        head.append((0x80 if mask else 0x00) | n)
    elif n < (1 << 16):
        head.append((0x80 if mask else 0x00) | 126)
        head += struct.pack(">H", n)
    else:
        head.append((0x80 if mask else 0x00) | 127)
        head += struct.pack(">Q", n)
    if mask:
        key = os.urandom(4)
        head += key
        data = bytes(b ^ key[i % 4] for i, b in enumerate(data))
    return bytes(head) + data


def ws_read_frame(recv: Callable[[int], bytes]) -> Optional[Tuple[int, bytes]]:
    """Read one WS frame from a recv()-like callable. Returns (opcode, payload)
    or None on clean EOF. Handles masking, 16/64-bit lengths, and control
    frames. Raises ValueError on protocol violations / oversized payloads."""
    hdr = _read_exactly(recv, 2)
    if hdr is None:
        return None
    b0, b1 = hdr[0], hdr[1]
    fin, opcode = b0 & 0x80, b0 & 0x0F
    masked, length = b1 & 0x80, b1 & 0x7F
    if not fin:
        raise ValueError("fragmented frames are not supported")
    if length == 126:
        length = struct.unpack(">H", _read_exactly(recv, 2))[0]  # type: ignore[arg-type]
    elif length == 127:
        length = struct.unpack(">Q", _read_exactly(recv, 8))[0]  # type: ignore[arg-type]
    if length > MAX_FRAME:
        raise ValueError("frame too large")
    key = _read_exactly(recv, 4) if masked else None  # type: ignore[assignment]
    payload = _read_exactly(recv, length) or b""
    if masked:
        payload = bytes(b ^ key[i % 4] for i, b in enumerate(payload))  # type: ignore[index]
    return opcode, payload


def _read_exactly(recv: Callable[[int], bytes], n: int) -> Optional[bytes]:
    buf = bytearray()
    while len(buf) < n:
        try:
            chunk = recv(min(n - len(buf), 65536))
        except (ConnectionError, socket.timeout, OSError):
            return None
        if not chunk:
            return None
        buf += chunk
    return bytes(buf)


# =============================================================================
# Client hub + simulation broadcast loop
# =============================================================================
_WS_SEND_LOCK = threading.Lock()  # serializes writes: pump thread + command threads share sockets


def _safe_send(sock: socket.socket, frame: bytes) -> None:
    with _WS_SEND_LOCK:
        sock.sendall(frame)


class Hub:
    """Registry of live WebSocket clients; broadcasts telemetry snapshots."""

    def __init__(self, sim: BengalWingsSim) -> None:
        self.sim = sim
        self._lock = threading.Lock()
        self._clients: List[socket.socket] = []

    def register(self, sock: socket.socket) -> None:
        with self._lock:
            self._clients.append(sock)

    def unregister(self, sock: socket.socket) -> None:
        with self._lock:
            if sock in self._clients:
                self._clients.remove(sock)

    @property
    def n_clients(self) -> int:
        return len(self._clients)

    def broadcast(self, obj: Dict[str, Any]) -> None:
        frame = ws_encode(json.dumps(obj, separators=(",", ":")))
        dead: List[socket.socket] = []
        with self._lock:
            clients = list(self._clients)
        for sock in clients:
            try:
                _safe_send(sock, frame)
            except OSError:
                dead.append(sock)
        if dead:
            with self._lock:
                for sock in dead:
                    if sock in self._clients:
                        self._clients.remove(sock)

    def pump(self, stop: threading.Event, hz: float) -> None:
        """Fixed-rate simulation pump: steps the physics and fans it out."""
        sim_dt = self.sim.dt
        interval = 1.0 / hz
        next_t = time.monotonic()
        while not stop.is_set():
            started = time.monotonic()
            n_steps = max(1, int(round(interval * self.sim.speed_mult / sim_dt)))
            for _ in range(n_steps):
                self.sim.step()
            self.broadcast(self.sim.snapshot())
            next_t += interval
            delay = next_t - time.monotonic()
            if delay > 0:
                stop.wait(delay)
            else:
                next_t = time.monotonic()


# =============================================================================
# HTTP handler: static dashboard + WS upgrade + JSON API
# =============================================================================
class GCSHandler(BaseHTTPRequestHandler):
    server_version = "BengalWingsGCS/1.0"
    protocol_version = "HTTP/1.1"

    # injected at class level by serve()
    hub: Hub = None  # type: ignore[assignment]
    sim: BengalWingsSim = None  # type: ignore[assignment]

    # ------------------------------------------------------------- helpers
    def _send(self, code: int, ctype: str, body: bytes, extra: Optional[Dict[str, str]] = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, code: int, obj: Dict[str, Any]) -> None:
        self._send(code, "application/json; charset=utf-8", json.dumps(obj).encode())

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length > 0 else b""

    # ----------------------------------------------------------- dispatch
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/ws/telemetry" and (self.headers.get("Upgrade") or "").lower() == "websocket":
            self._handle_ws_upgrade()
            return
        if path == "/api/telemetry":
            snap = dict(self.sim.snapshot())
            snap["clients"] = self.hub.n_clients
            self._send_json(200, snap)
            return
        if path == "/api/status":
            self._send_json(200, {"ok": True, "sim_time": round(self.sim.sim_time, 1),
                                  "mode": self.sim.mode, "clients": self.hub.n_clients,
                                  "engine": "bengal-wings/gcs"})
            return
        self._serve_static(path)

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/api/command":
            try:
                body = json.loads(self._read_body().decode("utf-8") or "{}")
                cmd = str(body.get("cmd", ""))
                args = {k: v for k, v in body.items() if k != "cmd"}
                result = self.sim.command(cmd, **args)
                self._send_json(200 if result == "ok" else 400, {"result": result})
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                self._send_json(400, {"result": f"bad request: {exc}"})
            return
        self._send(404, "text/plain; charset=utf-8", b"404 not found\n")

    # ----------------------------------------------------------- static UI
    def _serve_static(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        full = os.path.realpath(os.path.join(WEB_DIR, rel))
        if not full.startswith(os.path.realpath(WEB_DIR) + os.sep) or not os.path.isfile(full):
            self._send(404, "text/plain; charset=utf-8",
                       b"404 not found\nOpen this server at / for the dashboard.\n")
            return
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
            ctype += "; charset=utf-8"
        with open(full, "rb") as fh:
            self._send(200, ctype, fh.read())

    # ------------------------------------------------------------ websocket
    def _handle_ws_upgrade(self) -> None:
        key = self.headers.get("Sec-WebSocket-Key", "")
        if not key:
            self._send(400, "text/plain; charset=utf-8", b"missing Sec-WebSocket-Key\n")
            return
        accept = base64.b64encode(hashlib.sha1((key + WS_GUID).encode()).digest()).decode()
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()

        sock = self.connection
        sock.settimeout(90.0)  # clients heartbeat every 20 s to stay warm
        try:
            set_no_delay = getattr(socket, "TCP_NODELAY", None)
            if set_no_delay is not None:
                sock.setsockopt(socket.IPPROTO_TCP, set_no_delay, 1)
        except OSError:
            pass

        self.hub.register(sock)
        try:
            _safe_send(sock, ws_encode(json.dumps({"type": "hello", "sim": self.sim.snapshot()})))
            self._ws_serve_commands(sock)
        finally:
            self.hub.unregister(sock)
            self.close_connection = True

    def _ws_serve_commands(self, sock: socket.socket) -> None:
        while True:
            try:
                frame = ws_read_frame(sock.recv)
            except ValueError:
                break
            if frame is None:
                break
            opcode, payload = frame
            if opcode == 0x8:  # close
                try:
                    _safe_send(sock, ws_encode(payload, opcode=0x8))
                except OSError:
                    pass
                break
            if opcode == 0x9:  # ping → pong
                _safe_send(sock, ws_encode(payload, opcode=0xA))
                continue
            if opcode in (0x1, 0x2):
                try:
                    msg = json.loads(payload.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if msg.get("type") == "ping":  # app-level heartbeat
                    _safe_send(sock, ws_encode(json.dumps({"type": "pong"})))
                    continue
                cmd = str(msg.get("cmd", ""))
                if cmd:
                    args = {k: v for k, v in msg.items() if k != "cmd"}
                    result = self.sim.command(cmd, **args)
                    if result != "ok":
                        _safe_send(sock, ws_encode(json.dumps({"type": "cmd_ack", "cmd": cmd,
                                                               "result": result})))

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter console
        if os.environ.get("BENGAL_GCS_VERBOSE"):
            super().log_message(fmt, *args)


# =============================================================================
# Entry point
# =============================================================================
def serve(host: str = "0.0.0.0", port: int = 8090, hz: float = 10.0,
          seed: int = 2026, auto_demo: bool = True) -> ThreadingHTTPServer:
    sim = BengalWingsSim(seed=seed)
    if auto_demo:
        # Start a canned sortie so the dashboard is alive on first paint.
        sim.command("arm")
        sim.command("takeoff")
    hub = Hub(sim)
    GCSHandler.hub = hub
    GCSHandler.sim = sim

    httpd = ThreadingHTTPServer((host, port), GCSHandler)
    httpd.daemon_threads = True
    stop = threading.Event()

    def _loop() -> None:
        hub.pump(stop, hz)

    t = threading.Thread(target=_loop, name="gcs-pump", daemon=True)
    t.start()
    httpd._gcs_stop = stop  # type: ignore[attr-defined]
    return httpd


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="gcs", description="Bengal Wings GCS telemetry server")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--hz", type=float, default=10.0, help="telemetry broadcast rate")
    ap.add_argument("--seed", type=int, default=2026, help="simulation RNG seed")
    ap.add_argument("--no-auto-demo", action="store_true", help="start on the pad (disarmed)")
    args = ap.parse_args(argv)

    httpd = serve(args.host, args.port, args.hz, args.seed, auto_demo=not args.no_auto_demo)
    shown = "localhost" if args.host in ("0.0.0.0", "") else args.host
    print("==================================================================")
    print(" 🦅 BENGAL WINGS :: GROUND CONTROL STATION — Phase 1 Telemetry Core")
    print("==================================================================")
    print(f"   Dashboard   : http://{shown}:{args.port}/")
    print(f"   WS stream   : ws://{shown}:{args.port}/ws/telemetry  ({args.hz:g} Hz)")
    print(f"   HTTP poll   : http://{shown}:{args.port}/api/telemetry")
    print(f"   Sim seed    : {args.seed}   (SIMULATION ONLY — no live airframe link)")
    print("   Ctrl+C to shut down.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[GCS] shutdown requested — closing telemetry stream.")
    finally:
        getattr(httpd, "_gcs_stop", threading.Event()).set()
        httpd.shutdown()
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
