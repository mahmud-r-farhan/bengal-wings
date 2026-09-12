/* ============================================================================
   🦅 BENGAL WINGS GCS — dashboard logic (vanilla JS, zero dependencies)
   ----------------------------------------------------------------------------
   Primary link : WebSocket /ws/telemetry @10 Hz  (JSON frames)
   Fallback     : HTTP polling /api/telemetry     (if a proxy blocks WS)
   Commands     : WS text frames {cmd:...}  /  POST /api/command fallback
   ========================================================================== */
"use strict";

const RANGE_M = 160;                 // radar half-scale, meters
const $ = (id) => document.getElementById(id);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

/* ---------------------------------------------------------------- state -- */
let tel = null;                      // latest telemetry snapshot
let ws = null, wsAlive = false, pollTimer = null, reconnectTimer = null;
let lastMsgAt = 0;
const trail = [];                    // smoothed drone track
let view = { x: 0, y: 0 };           // rendered (lerped) drone position
let fps = 0, fpsAcc = 0, fpsN = 0;

/* ------------------------------------------------------------- link up -- */
function wsUrl() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${location.host}/ws/telemetry`;
}

function connect() {
  try { ws = new WebSocket(wsUrl()); } catch (e) { return startPolling(); }
  ws.onopen = () => { wsAlive = true; stopPolling(); setLink("WS LIVE", "good"); };
  ws.onmessage = (ev) => {
    lastMsgAt = performance.now();
    let msg; try { msg = JSON.parse(ev.data); } catch { return; }
    if (msg.type === "telemetry" || msg.type === "hello") onTelemetry(msg.type === "hello" ? msg.sim : msg);
  };
  ws.onclose = () => {
    wsAlive = false;
    setLink("RECONNECT…", "warn");
    startPolling();
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(connect, 2500);
  };
  ws.onerror = () => { try { ws.close(); } catch (e) {} };
}

setInterval(() => {
  if (wsAlive && ws && ws.readyState === 1) ws.send(JSON.stringify({ type: "ping" }));
  // if the socket looks open but is silent for 4 s, force the poll fallback
  if (performance.now() - lastMsgAt > 4000 && !pollTimer) startPolling();
}, 20000);

function startPolling() {
  if (pollTimer) return;
  setLink("HTTP POLL", "warn");
  pollTimer = setInterval(async () => {
    try {
      const r = await fetch("/api/telemetry", { cache: "no-store" });
      if (r.ok) { lastMsgAt = performance.now(); onTelemetry(await r.json()); }
    } catch (e) { setLink("LINK DOWN", "bad"); }
  }, 200);
}
function stopPolling() { clearInterval(pollTimer); pollTimer = null; }
function setLink(txt, cls) {
  const el = $("pill-link");
  el.textContent = `LINK: ${txt}`;
  el.className = `pill ${cls}`;
}

/* ------------------------------------------------------------- commands -- */
function sendCmd(obj) {
  const body = JSON.stringify(obj);
  if (wsAlive && ws && ws.readyState === 1) ws.send(body);
  else fetch("/api/command", { method: "POST", headers: { "Content-Type": "application/json" }, body })
    .then((r) => r.json())
    .then((j) => { if (j.result && j.result !== "ok") flash(j.result); });
}
document.querySelectorAll("#controls button[data-cmd]").forEach((b) =>
  b.addEventListener("click", () => sendCmd({ cmd: b.dataset.cmd })));
$("btn-jam").addEventListener("click", () => sendCmd({ cmd: "jam", on: !(tel && tel.gnss.jam) }));
$("btn-reset").addEventListener("click", () => sendCmd({ cmd: "reset", seed: Math.floor(Math.random() * 1e6) }));
$("rate").addEventListener("change", (e) => sendCmd({ cmd: "speed", mult: parseInt(e.target.value, 10) }));

window.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
  const map = { a: "arm", t: "takeoff", m: "mission", h: "hold", r: "rtl", l: "land", d: "disarm" };
  if (map[e.key]) sendCmd({ cmd: map[e.key] });
  if (e.key === "j") $("btn-jam").click();
});

/* --------------------------------------------------------- telemetry in -- */
function onTelemetry(s) {
  tel = s;
  pushTrail();
  renderPanels(s);
}

function pushTrail() {
  const p = [tel.nav.est.x, tel.nav.est.y];
  const last = trail[trail.length - 1];
  if (!last || Math.hypot(p[0] - last[0], p[1] - last[1]) > 0.35) {
    trail.push(p);
    if (trail.length > 1200) trail.shift();
  }
  if (!tel.flight && tel.pos.alt < 0.3 && trail.length && tel.tick % 100 === 0) trail.length = 0;
}

/* --------------------------------------------------------- panel render -- */
function renderPanels(s) {
  const g = (id) => $(id);
  const set = (id, v, cls = "") => { const el = g(id); el.textContent = v; el.className = cls; };
  set("t-mode", s.mode, s.mode === "STANDBY" ? "" : "hot");
  set("t-alt", s.pos.alt.toFixed(1) + " m");
  set("t-hdg", s.att.yaw.toFixed(0).padStart(3, "0") + "°");
  set("t-gs", s.vel.gs.toFixed(1) + " m/s");
  set("t-vs", (s.vel.vz >= 0 ? "+" : "") + s.vel.vz.toFixed(1) + " m/s", s.vel.vz > 0.3 ? "hot" : "");
  set("t-thr", s.att.throttle.toFixed(0) + " %");
  set("t-batt", s.batt.pct.toFixed(1) + " %", s.batt.pct < 25 ? "cold" : s.batt.pct < 40 ? "hot" : "");
  set("t-volt", s.batt.v.toFixed(2) + " V");
  set("t-cur", s.batt.a.toFixed(1) + " A");
  set("t-rssi", s.link.rssi.toFixed(0) + " dBm", s.link.rssi < -92 ? "cold" : "");
  set("t-loss", s.link.loss.toFixed(2) + " %", s.link.loss > 6 ? "cold" : "");
  set("t-rate", "10 Hz");
  set("t-nav", s.nav.source, s.nav.source.includes("RECKON") ? "cold" : "");
  set("t-hdop", s.nav.hdop.toFixed(2), s.nav.hdop > 2.5 ? "hot" : "");
  set("t-perr", s.nav.err.toFixed(2) + " m", s.nav.err > 0.8 ? "hot" : "");
  set("t-xy", `${s.pos.x >= 0 ? "+" : ""}${s.pos.x.toFixed(1)} / ${s.pos.y >= 0 ? "+" : ""}${s.pos.y.toFixed(1)} m`);

  // battery bar
  const fill = g("batt-fill");
  fill.style.width = s.batt.pct.toFixed(1) + "%";
  fill.className = s.batt.pct < 15 ? "crit" : s.batt.pct < 30 ? "low" : "";

  // pills
  const arm = g("pill-arm");
  arm.textContent = `ARM: ${s.armed ? "ARMED" : "SAFE"}`;
  arm.className = `pill ${s.armed ? "warn" : "good"}`;
  const gn = g("pill-gnss");
  gn.textContent = `GNSS: ${s.gnss.ok ? "LOCK" : "JAMMED"}`;
  gn.className = `pill ${s.gnss.ok ? "good" : "bad"}`;
  g("jam-banner").classList.toggle("on", !!s.gnss.jam);
  g("btn-jam").classList.toggle("active", !!s.gnss.jam);
  g("sim-clock").textContent = s.t.toFixed(1);
  const ai = g("ai-state");
  ai.textContent = s.flight ? "SCANNING ACTIVE" : "SENSOR STANDBY";
  ai.style.color = s.flight ? "" : "var(--dim)";

  // LALS anchors
  const lt = document.querySelector("#lals-table tbody");
  lt.innerHTML = s.anchors.map((a) => `
    <tr><td>${a.name}</td><td>${a.range != null ? a.range.toFixed(1) + " m" : "—"}</td>
    <td><span class="qbar ${a.q < 0.65 ? "degraded" : ""}"><i style="width:${(a.q * 100).toFixed(0)}%"></i></span></td>
    <td class="${a.q < 0.65 ? "st-deg" : "st-ok"}">${a.q < 0.65 ? "DEGRADED" : "SYNC"}</td></tr>`).join("");

  // contacts
  const ct = document.querySelector("#contacts-table tbody");
  ct.innerHTML = s.contacts.length ? s.contacts.slice().reverse().map((c) => `
    <tr class="p-${c.prio}"><td>#${c.id}</td><td>${c.cls}</td><td>${c.rng.toFixed(0)} m</td>
    <td>${c.brg.toFixed(0).padStart(3, "0")}°</td><td>${c.conf.toFixed(2)}</td>
    <td class="${c.prio === "CRITICAL" ? "st-crit" : c.prio === "HIGH" ? "st-deg" : ""}">${c.prio}</td></tr>`).join("")
    : `<tr><td colspan="6" class="empty-note">no contacts on the grid — airborne AI scan armed on takeoff</td></tr>`;

  // console log
  const list = g("log-list");
  const sig = s.log.length ? `${s.log[s.log.length - 1].t}:${s.log.length}:${s.log[s.log.length - 1].msg}` : "0";
  if (list.dataset.sig !== sig) {
    list.dataset.sig = sig;
    list.innerHTML = s.log.slice(-14).reverse().map((l) =>
      `<li><span class="tg t-${l.level}">[${l.level}]</span><span>T+${l.t}s ${l.msg}</span></li>`).join("");
  }
}

/* ----------------------------------------------------------- radar draw -- */
const radar = $("radar"), rctx = radar.getContext("2d");
let sweep = 0, lastFrame = performance.now();

function fitCanvas(cv) {
  const dpr = window.devicePixelRatio || 1;
  const r = cv.getBoundingClientRect();
  if (cv.width !== Math.round(r.width * dpr) || cv.height !== Math.round(r.height * dpr)) {
    cv.width = Math.round(r.width * dpr); cv.height = Math.round(r.height * dpr);
  }
  const ctx = cv.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { w: r.width, h: r.height };
}

function drawRadar(dt) {
  const { w, h } = fitCanvas(radar);
  const cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2 - 14;
  const scale = R / RANGE_M;
  const X = (x) => cx + x * scale;               // world → screen (east +)
  const Y = (y) => cy - y * scale;                // north +
  rctx.clearRect(0, 0, w, h);

  rctx.save();
  rctx.beginPath(); rctx.arc(cx, cy, R, 0, 7); rctx.clip();
  rctx.fillStyle = "#04070f"; rctx.fillRect(cx - R, cy - R, 2 * R, 2 * R);

  // grid
  rctx.strokeStyle = "rgba(0,255,204,.10)"; rctx.lineWidth = 1;
  for (let gx = -RANGE_M; gx <= RANGE_M; gx += 20) {
    rctx.beginPath(); rctx.moveTo(X(gx), Y(-RANGE_M)); rctx.lineTo(X(gx), Y(RANGE_M)); rctx.stroke();
    rctx.beginPath(); rctx.moveTo(X(-RANGE_M), Y(gx)); rctx.lineTo(X(RANGE_M), Y(gx)); rctx.stroke();
  }
  // range rings
  rctx.strokeStyle = "rgba(0,255,204,.22)";
  for (let r = 40; r <= RANGE_M; r += 40) {
    rctx.beginPath(); rctx.arc(cx, cy, r * scale, 0, 7); rctx.stroke();
    rctx.fillStyle = "rgba(0,255,204,.4)"; rctx.font = "10px monospace";
    rctx.fillText(`${r}m`, cx + 4, cy - r * scale + 12);
  }
  // crosshair + N marker
  rctx.beginPath(); rctx.moveTo(cx - 8, cy); rctx.lineTo(cx + 8, cy); rctx.moveTo(cx, cy - 8); rctx.lineTo(cx, cy + 8);
  rctx.strokeStyle = "rgba(0,255,204,.5)"; rctx.stroke();
  rctx.fillStyle = "#00ffcc"; rctx.font = "bold 12px monospace"; rctx.fillText("N", cx - 4, cy - R + 12);

  // LALS anchors: marker + live ranging arc to the drone estimate
  if (tel) {
    for (const a of tel.anchors) {
      rctx.strokeStyle = a.q < 0.65 ? "rgba(255,179,71,.55)" : "rgba(77,159,255,.5)";
      if (a.q < 0.65) rctx.setLineDash([3, 4]);
      rctx.beginPath(); rctx.arc(X(a.x), Y(a.y), (a.range || 0) * scale, 0, 7); rctx.stroke();
      rctx.setLineDash([]);
      rctx.fillStyle = a.q < 0.65 ? "#ffb347" : "#4d9fff";
      rctx.fillRect(X(a.x) - 4, Y(a.y) - 4, 8, 8);
      rctx.fillStyle = "rgba(185,232,221,.8)"; rctx.font = "10px monospace";
      rctx.fillText(a.name, X(a.x) + 7, Y(a.y) - 6);
    }
    // planned route + waypoints
    const wps = tel.wpt.list;
    if (wps.length) {
      rctx.strokeStyle = "rgba(0,255,204,.35)"; rctx.setLineDash([5, 4]);
      rctx.beginPath(); rctx.moveTo(X(view.x), Y(view.y));
      wps.forEach((p) => rctx.lineTo(X(p[0]), Y(p[1])));
      rctx.stroke(); rctx.setLineDash([]);
      wps.forEach((p, i) => {
        const done = i < tel.wpt.index, cur = i === tel.wpt.index;
        rctx.strokeStyle = done ? "rgba(0,255,204,.35)" : cur ? "#00ffcc" : "rgba(0,255,204,.7)";
        rctx.lineWidth = cur ? 2 : 1;
        rctx.strokeRect(X(p[0]) - 5, Y(p[1]) - 5, 10, 10);
        rctx.fillStyle = "rgba(0,255,204,.75)"; rctx.font = "9px monospace";
        rctx.fillText(`W${i + 1}${done ? "✓" : ""}`, X(p[0]) + 8, Y(p[1]) + 10);
      });
      rctx.lineWidth = 1;
    }
    // trail
    if (trail.length > 1) {
      rctx.strokeStyle = "rgba(0,255,204,.4)";
      rctx.beginPath(); rctx.moveTo(X(trail[0][0]), Y(trail[0][1]));
      for (const p of trail) rctx.lineTo(X(p[0]), Y(p[1]));
      rctx.stroke();
    }
    // AI contacts
    for (const c of tel.contacts) {
      const wx = tel.pos.x + c.rng * Math.sin(c.brg * Math.PI / 180);
      const wy = tel.pos.y + c.rng * Math.cos(c.brg * Math.PI / 180);
      const col = c.prio === "CRITICAL" ? "#ff4d6d" : c.prio === "HIGH" ? "#ffb347" : "rgba(185,232,221,.55)";
      rctx.fillStyle = col;
      const px = X(wx), py = Y(wy), s2 = 5;
      rctx.beginPath(); rctx.moveTo(px, py - s2); rctx.lineTo(px + s2, py); rctx.lineTo(px, py + s2); rctx.lineTo(px - s2, py); rctx.closePath(); rctx.fill();
      if (c.prio !== "LOW") { rctx.strokeStyle = col; rctx.globalAlpha = .35 + .3 * Math.sin(tel.t * 4); rctx.beginPath(); rctx.arc(px, py, 9, 0, 7); rctx.stroke(); rctx.globalAlpha = 1; }
      rctx.font = "9px monospace"; rctx.fillStyle = col;
      rctx.fillText(c.cls.split(" ")[0] + " #" + c.id, px + 8, py - 6);
    }
    // drone icon at EKF estimate + error circle
    const dx = X(view.x), dy = Y(view.y);
    const errR = Math.max(2.5, tel.nav.err * scale * 3);
    rctx.strokeStyle = "rgba(0,255,204,.5)"; rctx.setLineDash([2, 3]);
    rctx.beginPath(); rctx.arc(dx, dy, errR, 0, 7); rctx.stroke(); rctx.setLineDash([]);
    rctx.save(); rctx.translate(dx, dy); rctx.rotate(((tel.att.yaw - 90) * Math.PI) / 180);
    rctx.fillStyle = "#00ffcc"; rctx.shadowColor = "#00ffcc"; rctx.shadowBlur = 12;
    rctx.beginPath(); rctx.moveTo(9, 0); rctx.lineTo(-6, 5); rctx.lineTo(-3, 0); rctx.lineTo(-6, -5); rctx.closePath(); rctx.fill();
    rctx.restore();
    rctx.fillStyle = "rgba(0,255,204,.9)"; rctx.font = "10px monospace";
    rctx.fillText(`AEGIS-01 · ALT ${tel.pos.alt.toFixed(0)}m`, dx + 12, dy + 4);
  }

  // sweep
  sweep += dt * 0.9;
  rctx.save(); rctx.translate(cx, cy);
  for (let i = 0; i < 46; i++) {
    const a = sweep - i * 0.014;
    rctx.strokeStyle = `rgba(0,255,204,${0.16 * (1 - i / 46)})`;
    rctx.beginPath(); rctx.moveTo(0, 0); rctx.lineTo(R * Math.cos(a), R * Math.sin(a)); rctx.stroke();
  }
  rctx.restore();
  rctx.restore();

  // scope bezel
  rctx.strokeStyle = "rgba(0,255,204,.65)"; rctx.lineWidth = 1.5;
  rctx.beginPath(); rctx.arc(cx, cy, R, 0, 7); rctx.stroke(); rctx.lineWidth = 1;
}

radar.addEventListener("click", (e) => {
  const r = radar.getBoundingClientRect();
  const cx = r.width / 2, cy = r.height / 2, R = Math.min(r.width, r.height) / 2 - 14;
  const scale = R / RANGE_M;
  const x = (e.clientX - r.left - cx) / scale;
  const y = (cy - (e.clientY - r.top)) / scale;
  if (Math.hypot(x, y) <= RANGE_M && tel) sendCmd({ cmd: "goto", x: +x.toFixed(1), y: +y.toFixed(1) });
});

/* -------------------------------------------------------- attitude view -- */
const att = $("att"), actx = att.getContext("2d");

function drawAttitude() {
  const { w, h } = fitCanvas(att);
  actx.clearRect(0, 0, w, h);
  const cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2 - 6;
  const s = tel || { att: { roll: 0, pitch: 0, yaw: 0 }, mode: "—" };
  actx.save();
  actx.beginPath(); actx.arc(cx, cy, R, 0, 7); actx.clip();
  actx.translate(cx, cy);
  actx.rotate((-s.att.roll * Math.PI) / 180);
  const px = (s.att.pitch * 2.6);
  // sky / ground
  actx.fillStyle = "#0d3a5c"; actx.fillRect(-2 * R, -2 * R + px, 4 * R, 2 * R);
  actx.fillStyle = "#3b2c14"; actx.fillRect(-2 * R, px, 4 * R, 2 * R);
  actx.strokeStyle = "#00ffcc"; actx.beginPath(); actx.moveTo(-2 * R, px); actx.lineTo(2 * R, px); actx.stroke();
  // pitch ladder
  actx.strokeStyle = "rgba(0,255,204,.6)"; actx.fillStyle = "rgba(0,255,204,.8)";
  actx.font = "8px monospace"; actx.textAlign = "center";
  for (let p = -30; p <= 30; p += 10) {
    if (!p) continue;
    const yy = px - p * 2.6, lw = Math.abs(p) % 20 === 0 ? 34 : 18;
    actx.beginPath(); actx.moveTo(-lw, yy); actx.lineTo(lw, yy); actx.stroke();
    if (Math.abs(p) % 20 === 0) { actx.fillText(String(Math.abs(p)), -lw - 10, yy + 3); actx.fillText(String(Math.abs(p)), lw + 10, yy + 3); }
  }
  actx.restore();
  // fixed aircraft symbol
  actx.strokeStyle = "#ffe066"; actx.lineWidth = 2;
  actx.beginPath(); actx.moveTo(cx - 26, cy); actx.lineTo(cx - 8, cy); actx.moveTo(cx + 8, cy); actx.lineTo(cx + 26, cy);
  actx.moveTo(cx, cy - 6); actx.lineTo(cx, cy - 2); actx.stroke();
  actx.fillStyle = "#ffe066"; actx.beginPath(); actx.arc(cx, cy, 2, 0, 7); actx.fill(); actx.lineWidth = 1;
  // roll pointer arc
  actx.strokeStyle = "rgba(0,255,204,.8)";
  actx.beginPath(); actx.arc(cx, cy, R - 2, -Math.PI / 2 - clamp(s.att.roll, -60, 60) * Math.PI / 180 - 0.02, -Math.PI / 2 - clamp(s.att.roll, -60, 60) * Math.PI / 180 + 0.02); actx.stroke();
  // heading readout
  actx.fillStyle = "rgba(0,255,204,.9)"; actx.font = "bold 13px monospace"; actx.textAlign = "center";
  actx.fillText(`${String(Math.round(s.att.yaw)).padStart(3, "0")}° HDG`, cx, cy + R + 1);
  actx.textAlign = "start";
}

/* --------------------------------------------------------------- loop ---- */
function loop(now) {
  const dt = Math.min(0.05, (now - lastFrame) / 1000) || 0.016;
  lastFrame = now;
  fpsAcc += dt; fpsN++;
  if (fpsAcc > 1) { fps = Math.round(fpsN / fpsAcc); fpsAcc = 0; fpsN = 0; }
  if (tel) {
    const k = 1 - Math.exp(-dt * 8);
    view.x += (tel.nav.est.x - view.x) * k;
    view.y += (tel.nav.est.y - view.y) * k;
  }
  drawRadar(dt);
  drawAttitude();
  $("utc-clock").textContent = new Date().toISOString().substr(11, 8);
  requestAnimationFrame(loop);
}

function flash(msg) { /* transient toast in console pill */
  setLink(msg.slice(0, 22), "warn");
  setTimeout(() => setLink(wsAlive ? "WS LIVE" : "HTTP POLL", wsAlive ? "good" : "warn"), 1200);
}

connect();
requestAnimationFrame(loop);
