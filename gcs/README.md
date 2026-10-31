# 🦅 Bengal Wings — GCS Core (`gcs/`)

> **Runnable software prototype:** zero-dependency Python telemetry server + browser dashboard for a deterministic flight/LALS/perception **simulation**. It does not connect to or control an aircraft; hardware and autonomy documentation is not field validation.

---

## ⚡ Quick Start

No `pip install`, no build toolchain — Python 3.9+ standard library only:

```bash
# From the repository root
python3 -m gcs                 # or: make gcs
# → Dashboard: http://localhost:8090/
```

Open the URL and the operator console comes up live: a simulated AEGIS-01 sortie
is already flying (auto-demo). Use `--no-auto-demo` to start on the pad, and
keyboard shortcuts `a r m / t a k e o f f / h o l d / r t l / l a n d` to fly it.

| Flag | Default | Purpose |
|---|---|---|
| `--port` | `8090` | HTTP/WS listen port |
| `--host` | `0.0.0.0` | Bind address (LAN/tactical network) |
| `--hz` | `10` | Telemetry broadcast rate |
| `--seed` | `2026` | Deterministic simulation seed (reproducible tests/demos) |

---

## Community response board

Open `http://localhost:8090/response.html` (or choose **COMMUNITY RESPONSE BOARD** from the simulator header) to use Shomoy / সময়. It is a standalone, mobile-friendly flood and community-emergency coordination board, not an airframe control panel.

- Record needs with urgency, location, affected people, access conditions and follow-up status; register nearby boats, transport, shelter, supplies or volunteer teams.
- Search/filter reports, assign a team, print the board, download a CSV, and export/import a JSON backup. Import merges records by reference ID.
- Reports live in this browser's `localStorage` only. There is **no login, server database, cloud sync or upload**. Each device/browser has a separate copy; exchange backups deliberately and reconcile duplicates with responders.
- The first visit must load the app shell while online for service-worker caching to work offline (HTTPS or localhost required by browsers). Local storage still works when internet is unavailable, but browser/device loss can destroy data—export backups to secure storage.
- GPS is opt-in after pressing the location button; coordinates are placed in the local form only. Avoid recording names, national IDs, private contact details or sensitive health information. Treat exports as sensitive.
- P1/P2/P3 are operator-selected prompts, **not a scored assessment or official dispatch priority**. Verify reports and coordinate urgent action with the Union/Upazila Disaster Management Committee and responsible emergency responders. The board provides no live alerts or rescue dispatch.

The field categories reflect needs highlighted in the [UN Bangladesh pre-crisis flood assessment](https://bangladesh.un.org/en/247856-pre-crisis-assessment-monsoon-flooding-bangladesh-humanitarian-coordination-task-team-hctt) (safe water, food, sanitation and other essential needs) and align with the coordination context in the Bangladesh [Department of Disaster Management Standing Orders](https://ddm.gov.bd/site/view/policies/%E0%A6%8F%E0%A6%B8%E0%A6%93%E0%A6%A1%E0%A6%BF%28SOD%29). These sources inform the tool; they are not live data feeds.

## 🧭 What It Simulates (maps 1:1 to `docs/`)

| Dashboard subsystem | Reference spec |
|---|---|
| Flight state machine (STANDBY → ARM → TAKEOFF → NAV → HOLD → RTL → LAND) | `docs/SOFTWARE_AND_FIRMWARE.md` §2 |
| LALS UWB anchor grid: 4 anchors, 2-way ToF ranging, altitude-projected 2D trilateration + EKF-lite estimate with growing σ under degraded links | `docs/LALS_MANUFACTURING_AND_TEST.md` §1 |
| GPS-denied behaviour: injecting jamming drops GNSS, logs the EW event, raises HDOP, and the vehicle keeps flying on LALS + optical flow (dead-reckons if the grid degrades below 3 anchors) | `README.md` master architecture |
| Edge-AI contacts: 6 threat classes, `conf > 0.75` alert gate, priority/action decision matrix (CRITICAL → anti-drone alert, HIGH → lock track + relay coords) | `docs/AI_AND_THREAT_DETECTION.md` §2, §4 |
| 6S 4500 mAh battery drain model, RSSI/frame-loss link model | `docs/HARDWARE_AND_PHYSICAL.md` §2 |

## 🔌 Wire Protocol

* `GET /` — tactical dashboard (static, `gcs/web/`).
* `WS /ws/telemetry` — 10 Hz JSON telemetry frames (`type: "telemetry"`),
  plus `hello` on connect and `cmd_ack` on rejected commands.
  Client frames: `{"cmd": "...", ...}` (masked, per RFC 6455). The framing
  layer is a stdlib-only implementation — see `server.py::ws_encode/ws_read_frame`.
* `GET /api/telemetry` — same snapshot over plain HTTP (automatic dashboard
  fallback when a proxy blocks WebSockets; also handy for curl debugging).
* `POST /api/command` — same command surface as the WS channel.
* `GET /api/status` — liveness probe.

Commands: `arm`, `disarm`, `takeoff`, `mission`, `hold`, `rtl`, `land`,
`goto {x,y}`, `jam {on}`, `speed {mult}`, `reset {seed}`.

## 🧱 Module Map

```
gcs/
├── __main__.py   # python3 -m gcs entry point
├── sim.py        # flight / LALS / AI-perception / power simulation core
├── server.py     # HTTP + RFC 6455 WebSocket telemetry server (stdlib only)
└── web/          # simulator dashboard + Shomoy response app (response.html/css/js/sw.js)
tests/
└── test_gcs.py   # 22 unit tests: trilateration math, state machine, codec
```

## 🛡️ Scope & Safety Note

This module is a **simulation and operator-UI reference implementation**. It
does not connect to, command, or interfere with any real aircraft, radio, or
sensor hardware. A production airframe link (encrypted MAVLink/DDS, per
`docs/SOFTWARE_AND_FIRMWARE.md`) would replace `sim.py` behind the identical
snapshot/command interface — which is exactly why the two are decoupled.
