# ==============================================================================
# 🦅 BENGAL WINGS :: GCS CORE — FLIGHT & NAVIGATION SIMULATION ENGINE
# ------------------------------------------------------------------------------
# Pure-Python, zero-dependency physics model powering the Phase 1 Ground
# Control Station demo. It simulates:
#
#   * AEGIS-CORE quad flight dynamics (position/velocity/attitude, NED-ish)
#   * Mission state machine (STANDBY → ARM → TAKEOFF → MISSION → HOLD → LAND)
#   * LALS UWB anchor network (2-way ToF ranging + 2D trilateration + EKF-lite
#     position estimate with error growth under degraded links / GNSS jamming)
#   * Edge-AI threat contacts (classes & decision matrix per
#     docs/AI_AND_THREAT_DETECTION.md)
#   * 6S battery drain, RF link quality (RSSI / frame loss), mission log
#
# Determinism: every random draw comes from a single seeded random.Random,
# so a given seed reproduces an identical flight (used by the unit tests).
#
# ⚠️  SIMULATION ONLY — this module never talks to real flight hardware.
# ==============================================================================
"""Bengal Wings GCS simulation core (stdlib only)."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

G_ACCEL = 9.81
CRUISE_SPEED = 8.0          # m/s horizontal in MISSION
RTL_SPEED = 11.0            # m/s return-to-launch cruise
CLIMB_RATE = 3.0            # m/s takeoff climb
DESCENT_RATE = 1.5          # m/s landing approach
TAKEOFF_ALT = 25.0          # m AGL mission altitude
CRUISE_ALT = 20.0           # m AGL during RTL pattern
WPT_RADIUS = 1.5            # m — "captured" threshold for a waypoint
MAX_TILT_DEG = 32.0         # attitude model clamp
RANGE_LIMIT_M = 160.0       # radar scope scale + AI sensor envelope

# Threat taxonomy mirrors docs/AI_AND_THREAT_DETECTION.md (yolo_recon.yaml).
THREAT_CLASSES: List[Dict[str, Any]] = [
    {"cls": "ARMED INFANTRY", "priority": "HIGH", "speed": 1.5},
    {"cls": "UNARMED HUMAN", "priority": "LOW", "speed": 1.2},
    {"cls": "ARMORED VEHICLE", "priority": "HIGH", "speed": 3.0},
    {"cls": "CIVILIAN VEHICLE", "priority": "LOW", "speed": 6.0},
    {"cls": "HOSTILE UAV", "priority": "CRITICAL", "speed": 9.0},
    {"cls": "WEAPON CACHE", "priority": "HIGH", "speed": 0.0},
]

# Decision matrix actions (docs/AI_AND_THREAT_DETECTION.md §4).
PRIORITY_ACTION = {
    "CRITICAL": "ALERT ANTI-DRONE GRID",
    "HIGH": "LOCK TRACK · RELAY COORDS",
    "LOW": "MONITOR · CONTINUE SCAN",
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


@dataclass
class Anchor:
    """One LALS UWB ground beacon (high-mast). z is mast height in meters."""
    name: str
    x: float
    y: float
    z: float
    quality: float = 1.0     # 0..1 composite link quality (FOV/multipath)

    @property
    def degraded(self) -> bool:
        return self.quality < 0.65


def trilaterate_2d(anchors: List[Tuple[float, float, float]],
                   dists: List[float], z_ref: float) -> Optional[Tuple[float, float]]:
    """Classic 2D trilateration given slant ranges and a known altitude.

    For each anchor i we project its slant range r_i down to the drone's
    altitude plane: d_i^2 = r_i^2 - (z_ref - z_i)^2. Subtracting the sphere
    equations pairwise yields two linear equations in (x, y).

    Returns (x, y) or None when anchors are degenerate (collinear) or a
    projected range is imaginary. Uses the first three anchors supplied.
    """
    if len(anchors) < 3 or len(dists) < 3:
        return None
    dd: List[float] = []
    for (ax, ay, az), r in zip(anchors[:3], dists[:3]):
        v = r * r - (z_ref - az) ** 2
        if v < 0:
            return None
        dd.append(v)
    (ax, ay, _), (bx, by, _), (cx, cy, _) = anchors[0], anchors[1], anchors[2]
    d2x, d2y = 2.0 * (bx - ax), 2.0 * (by - ay)
    d3x, d3y = 2.0 * (cx - ax), 2.0 * (cy - ay)
    det = d2x * d3y - d3x * d2y
    if abs(det) < 1e-9:
        return None
    k1 = (bx * bx + by * by - ax * ax - ay * ay) + (dd[0] - dd[1])
    k2 = (cx * cx + cy * cy - ax * ax - ay * ay) + (dd[0] - dd[2])
    x = (k1 * d3y - k2 * d2y) / det
    y = (d2x * k2 - d3x * k1) / det
    return x, y


@dataclass
class Contact:
    """An Edge-AI detection tracked in polar (drone-relative) coordinates."""
    tid: int
    cls: str
    priority: str
    bearing_deg: float
    range_m: float
    radial_ms: float          # + = closing
    heading_deg: float        # contact ground track (for UI arrows)
    conf: float
    ttl: float

    def step(self, dt: float) -> None:
        self.range_m = max(4.0, self.range_m - self.radial_ms * dt)
        self.ttl -= dt


@dataclass
class BengalWingsSim:
    """Stateful simulation ticking at a fixed timestep."""
    seed: int = 2026
    rng: random.Random = field(default_factory=random.Random, repr=False)
    dt: float = 0.05
    sim_time: float = 0.0
    tick: int = 0

    # --- flight state ----------------------------------------------------
    mode: str = "STANDBY"
    armed: bool = False
    pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)      # NED x,y,alt
    vel: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    throttle: float = 0.0
    waypoints: List[Tuple[float, float]] = field(default_factory=list)
    wpt_index: int = 0
    home: Tuple[float, float] = (0.0, 0.0)

    # --- power / link ----------------------------------------------------
    batt_pct: float = 100.0
    pack_v: float = 25.2
    current_a: float = 0.6
    rssi_dbm: float = -48.0
    frame_loss_pct: float = 0.0
    gnss_ok: bool = True
    jam_injected: bool = False

    # --- LALS / navigation estimator --------------------------------------
    anchors: List[Anchor] = field(default_factory=list)
    anchor_ranges: List[float] = field(default_factory=list)
    est_pos: Tuple[float, float] = (0.0, 0.0)
    pos_err_m: float = 0.0
    hdop: float = 0.9
    nav_source: str = "LALS + OPTICAL FLOW"

    # --- perception / logs ------------------------------------------------
    contacts: List[Contact] = field(default_factory=list)
    next_contact_id: int = 1
    contact_cooldown: float = 3.0
    log: List[Dict[str, Any]] = field(default_factory=list)

    # --- tunables exposed to the UI ----------------------------------------
    speed_mult: int = 1
    flight_active: bool = False   # armed & airborne (spawns contacts, drains)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.anchors = [
            Anchor("A1", -45.0, 45.0, 6.0),
            Anchor("A2", 45.0, 45.0, 6.0),
            Anchor("A3", 45.0, -45.0, 6.0),
            Anchor("A4", -45.0, -45.0, 6.0),
        ]
        # Default sortie: 4-point box survey pattern.
        self.waypoints = [(-60.0, 60.0), (60.0, 60.0), (60.0, -60.0), (-60.0, -60.0)]
        self._push_log("SIM", f"AEGIS-CORE sim online (seed={self.seed}) — SIMULATION ONLY")

    # ------------------------------------------------------------------ log
    def _push_log(self, level: str, msg: str) -> None:
        self.log.append({"t": round(self.sim_time, 1), "level": level, "msg": msg})
        if len(self.log) > 60:
            del self.log[:-60]

    # ------------------------------------------------------------- commands
    def command(self, cmd: str, **args: Any) -> str:
        """Apply an operator command from the GCS UI. Returns 'ok' or error."""
        c = (cmd or "").lower()
        if c == "arm":
            if not self.armed and self.mode == "STANDBY":
                self.armed = True
                self.mode = "ARMED"
                self._push_log("CMD", "FCU ARMED — pre-flight checks PASSED (EKF: LALS/OF)")
        elif c == "disarm":
            if self.pos[2] < 0.5 and self.mode in ("STANDBY", "ARMED", "LAND"):
                self.armed = False
                self.flight_active = False
                self.mode = "STANDBY"
                self.throttle = 0.0
                self._push_log("CMD", "DISARMED — props stopped")
            else:
                self._push_log("WARN", "DISARM rejected: land the vehicle first")
                return "denied: airborne"
        elif c == "takeoff":
            if self.armed and self.pos[2] < 0.5:
                self.mode = "TAKEOFF"
                self.flight_active = True
                self._push_log("CMD", f"AUTO TAKEOFF → {TAKEOFF_ALT:.0f} m AGL")
        elif c == "mission":
            if self.armed and self.mode in ("HOLD", "TAKEOFF", "NAV"):
                self.mode = "NAV"
                self.wpt_index = 0
                self._push_log("CMD", f"MISSION START — {len(self.waypoints)} waypoints")
        elif c == "hold":
            if self.flight_active and self.mode in ("NAV", "TAKEOFF", "RTL"):
                self.mode = "HOLD"
                self._push_log("CMD", "POSITION HOLD — station-keeping on LALS fix")
        elif c == "rtl":
            if self.flight_active and self.mode != "RTL":
                self.mode = "RTL"
                self._push_log("CMD", "RTL — climbing to cruise, homing on LALS anchor A-grid")
        elif c == "land":
            if self.flight_active and self.mode not in ("LAND",):
                self.mode = "LAND"
                self._push_log("CMD", "DESCENT — vertical speed -{:.1f} m/s".format(DESCENT_RATE))
        elif c == "goto":
            x = _clamp(float(args.get("x", 0.0)), -RANGE_LIMIT_M, RANGE_LIMIT_M)
            y = _clamp(float(args.get("y", 0.0)), -RANGE_LIMIT_M, RANGE_LIMIT_M)
            self.waypoints.append((x, y))
            if self.flight_active and self.mode in ("HOLD", "NAV"):
                self.mode = "NAV"
                self._push_log("CMD", f"NEW WPT #{len(self.waypoints)} @ ({x:+.1f}, {y:+.1f}) — re-tasking")
            else:
                self._push_log("CMD", f"WPT #{len(self.waypoints)} @ ({x:+.1f}, {y:+.1f}) queued")
        elif c == "jam":
            self.jam_injected = bool(args.get("on", False))
            self._push_log("EW", "GNSS JAMMING SIGNAL INJECTED — GPS DENIED" if self.jam_injected
                           else "GNSS REACQUIRED — jamming ceased")
        elif c == "speed":
            self.speed_mult = int(_clamp(float(args.get("mult", 1)), 1, 4))
            self._push_log("CMD", f"SIM RATE → {self.speed_mult}x")
        elif c == "reset":
            seed = int(args.get("seed", self.seed))
            self.reset(seed)
        else:
            return f"unknown command: {cmd}"
        return "ok"

    def reset(self, seed: Optional[int] = None) -> None:
        if seed is None:
            seed = self.seed
        keep_speed = self.speed_mult
        self.__init__(seed=seed, speed_mult=keep_speed)  # type: ignore[misc]

    # ----------------------------------------------------------------- step
    def step(self) -> None:
        """Advance the world by dt seconds (one fixed-rate tick)."""
        dt = self.dt
        self.sim_time += dt
        self.tick += 1

        self._update_flight(dt)
        self._update_attitude(dt)
        self._update_power(dt)
        self._update_link(dt)
        self._update_lals(dt)
        self._update_contacts(dt)

    # ------------------------------------------------------------ flight ---
    def _update_flight(self, dt: float) -> None:
        x, y, z = self.pos
        vx, vy, vz = self.vel
        tx: Optional[Tuple[float, float]] = None
        t_alt = 0.0
        vmax = CRUISE_SPEED

        if self.mode == "ARMED":
            t_alt = 0.0
        elif self.mode == "TAKEOFF":
            t_alt = TAKEOFF_ALT
        elif self.mode == "NAV":
            t_alt = TAKEOFF_ALT
            if self.wpt_index < len(self.waypoints):
                tx = self.waypoints[self.wpt_index]
                dx, dy = tx[0] - x, tx[1] - y
                if math.hypot(dx, dy) < WPT_RADIUS:
                    self._push_log("NAV", f"WPT #{self.wpt_index + 1} captured ({tx[0]:+.0f}, {tx[1]:+.0f})")
                    self.wpt_index += 1
                    if self.wpt_index >= len(self.waypoints):
                        self.mode = "HOLD"
                        self._push_log("NAV", "SURVEY PATTERN COMPLETE — entering HOLD")
                    else:
                        tx = self.waypoints[self.wpt_index]
            else:
                self.mode = "HOLD"
        elif self.mode == "HOLD":
            t_alt = TAKEOFF_ALT
            tx = (x, y)
        elif self.mode == "RTL":
            t_alt = CRUISE_ALT
            vmax = RTL_SPEED
            hx, hy = self.home
            if math.hypot(hx - x, hy - y) < 2.0:
                self.mode = "LAND"
                self._push_log("NAV", "HOME POINT REACHED — final descent")
            else:
                tx = (hx, hy)
        elif self.mode == "LAND":
            t_alt = 0.0

        # Horizontal velocity command toward target.
        ax_c = ay_c = 0.0
        if tx is not None and self.mode != "ARMED":
            dx, dy = tx[0] - x, tx[1] - y
            dist = math.hypot(dx, dy)
            if dist > 1e-6:
                desired = min(vmax, math.sqrt(2.0 * 3.0 * dist))  # accel-limited profile
                vx_c, vy_c = desired * dx / dist, desired * dy / dist
                ax_c, ay_c = (vx_c - vx) / dt, (vy_c - vy) / dt
                a_max = 4.0 * dt
                vx += _clamp(vx_c - vx, -a_max, a_max)
                vy += _clamp(vy_c - vy, -a_max, a_max)
            else:
                vx *= 0.9
                vy *= 0.9
        else:
            vx *= 0.88
            vy *= 0.88

        # Vertical channel.
        z_err = t_alt - z
        vz_c = _clamp(z_err * 1.2, -DESCENT_RATE if self.mode == "LAND" else -CLIMB_RATE, CLIMB_RATE)
        if abs(z_err) < 0.25 and (self.mode != "LAND" or t_alt > 1.0):
            vz_c = 0.0  # soft-capture at cruise altitude; never while landing
        vz += _clamp(vz_c - vz, -2.0 * dt, 2.0 * dt)
        z = max(0.0, z + vz * dt)
        if self.mode == "LAND" and z <= 0.2 and vz <= 0.0:
            # PX4-style touchdown detection: below threshold, cut and disarm.
            z, vz = 0.0, 0.0
            self.armed = False
            self.flight_active = False
            self.mode = "STANDBY"
            self._push_log("NAV", "TOUCHDOWN — auto-disarmed, FCU standby")
        elif z <= 0.0:
            z, vz = 0.0, 0.0  # ground clamp: never sink below the pad plane

        x += vx * dt
        y += vy * dt
        self.pos = (round(x, 3), round(y, 3), round(z, 3))
        self.vel = (round(vx, 3), round(vy, 3), round(vz, 3))

        if self.mode in ("TAKEOFF",) and z >= TAKEOFF_ALT - 0.3:
            self.mode = "NAV" if self.waypoints else "HOLD"
            if self.mode == "NAV":
                self.wpt_index = 0
                self._push_log("NAV", f"Climb complete → MISSION ({len(self.waypoints)} wp survey box)")

        # Yaw steers toward the current target (hold/standby: keep heading).
        if tx is not None and self.mode in ("NAV", "RTL") :
            want = math.degrees(math.atan2(tx[1] - y, tx[0] - x)) % 360.0
            err = (want - self.yaw_deg + 540.0) % 360.0 - 180.0
            self.yaw_deg = (self.yaw_deg + _clamp(err * 0.10, -45.0 * dt, 45.0 * dt)) % 360.0

        self.throttle = (0.0 if not self.armed else
                         _clamp(0.42 + 0.10 * max(0.0, vz) + 0.03 * math.hypot(vx, vy)
                                + (0.0 if z <= 0.0 else 0.18), 0.0, 0.95))

    def _update_attitude(self, dt: float) -> None:
        """Body attitude follows the velocity command (tilt-to-fly quad model).

        Horizontal velocity is projected into the body frame; the tilt needed
        to sustain it drives the pitch/roll command, low-passed for realism.
        """
        vx, vy, _ = self.vel
        yaw = math.radians(self.yaw_deg)
        v_fwd = vx * math.cos(yaw) + vy * math.sin(yaw)
        v_lat = -vx * math.sin(yaw) + vy * math.cos(yaw)
        pitch_cmd = _clamp(-v_fwd * 2.2, -MAX_TILT_DEG, MAX_TILT_DEG)
        roll_cmd = _clamp(v_lat * 2.2, -MAX_TILT_DEG, MAX_TILT_DEG)
        if self.mode not in ("NAV", "RTL", "TAKEOFF", "LAND"):
            pitch_cmd *= 0.15
            roll_cmd *= 0.15
        wob = (self.rng.random() - 0.5) * (2.4 if self.armed else 0.2)
        self.pitch_deg = round(_clamp(self.pitch_deg + 0.18 * (pitch_cmd - self.pitch_deg) + wob * 0.15, -40, 40), 2)
        self.roll_deg = round(_clamp(self.roll_deg + 0.18 * (roll_cmd - self.roll_deg) + wob * 0.15, -40, 40), 2)

    # ------------------------------------------------------- power / link ---
    def _update_power(self, dt: float) -> None:
        if self.armed:
            base = 4.0 if self.pos[2] <= 0.05 else 12.0
            load = base + 6.0 * min(1.0, math.hypot(self.vel[0], self.vel[1]) / CRUISE_SPEED) + 4.5 * self.throttle
            self.current_a = round(_clamp(load + (self.rng.random() - 0.5) * 0.8 + 1.2, 3.0, 60.0), 2)
        else:
            self.current_a = round(0.55 + (self.rng.random() - 0.5) * 0.1, 2)
        used_mah = self.current_a * dt / 3.6  # 4500 mAh pack
        self.batt_pct = max(0.0, self.batt_pct - used_mah / 4500.0 * 100.0)
        frac = self.batt_pct / 100.0
        cell = 3.50 + 0.70 * (frac ** 1.25)
        sag = self.current_a * 0.0105
        self.pack_v = round(max(19.8, (cell * 6.0) - sag), 2)
        if not self._warned and self.batt_pct < 25.0:
            self._push_log("WARN", "BATTERY 25% — RTN threshold reached, plan RTL")
            self._warned = True
        if self._warned and self.batt_pct >= 30.0:
            self._warned = False

    _warned = False

    def _update_link(self, dt: float) -> None:
        dist = math.hypot(self.pos[0], self.pos[1])
        target = -50.0 - 0.11 * dist - (6.0 if self.jam_injected else 0.0)
        self.rssi_dbm = round(_clamp(self.rssi_dbm + (target - self.rssi_dbm) * 0.15
                                     + (self.rng.random() - 0.5) * 1.4, -108.0, -32.0), 1)
        base_loss = 0.2 + (4.5 if self.jam_injected else 0.0) + max(0.0, (abs(self.rssi_dbm) - 95.0) * 0.12)
        self.frame_loss_pct = round(_clamp(self.frame_loss_pct * 0.8 + base_loss * 0.2
                                           + max(0.0, self.rng.gauss(0, 0.15)), 0.0, 30.0), 2)

    # --------------------------------------------------------------- LALS ---
    def _update_lals(self, dt: float) -> None:
        x, y, z = self.pos
        self.anchor_ranges = []
        for a in self.anchors:
            a.quality = _clamp(a.quality + self.rng.gauss(0.0, 0.012) + (0.0006 if a.quality < 0.98 else 0.0), 0.35, 1.0)
            r = math.sqrt(max(0.0, (a.x - x) ** 2 + (a.y - y) ** 2 + (a.z - z) ** 2))
            self.anchor_ranges.append(round(r, 2))

        online = [a for a in self.anchors if not a.degraded]
        usable = len(online) >= 3
        sigma = 0.085 / max(0.45, (sum(a.quality for a in online) / max(1, len(online))) if usable else 0.5)
        if self.jam_injected:
            sigma += 0.05
        tri: Optional[Tuple[float, float]] = None
        if usable:
            pick = online[:3]
            pick_idx = [i for i, a in enumerate(self.anchors) if not a.degraded][:3]
            tri = trilaterate_2d([(a.x, a.y, a.z) for a in pick],
                                 [self.anchor_ranges[i] for i in pick_idx], z)
        if tri is not None:
            ex = tri[0] + self.rng.gauss(0.0, sigma)
            ey = tri[1] + self.rng.gauss(0.0, sigma)
            self.est_pos = (round(ex, 2), round(ey, 2))
        else:
            # EKF dead-reckoning on optical flow when the UWB grid is lost.
            self.est_pos = (round(self.est_pos[0] + self.vel[0] * dt + self.rng.gauss(0, 0.25), 2),
                            round(self.est_pos[1] + self.vel[1] * dt + self.rng.gauss(0, 0.25), 2))
        self.pos_err_m = round(math.hypot(self.est_pos[0] - x, self.est_pos[1] - y), 2)

        degraded_n = sum(1 for a in self.anchors if a.degraded)
        self.hdop = round(_clamp(0.85 + degraded_n * 1.15 + (0.45 if not usable else 0.0)
                                 + (0.35 if self.jam_injected else 0.0) + abs(self.rng.gauss(0, 0.05)), 0.6, 9.9), 2)
        new_src = ("LALS + OPTICAL FLOW" if usable else "OPTICAL FLOW DEAD RECKON")
        if new_src != self.nav_source:
            self.nav_source = new_src
            self._push_log("EKF", f"Nav source → {new_src}")
        if self.gnss_ok and self.jam_injected:
            self.gnss_ok = False
            self._push_log("EW", "GNSS LOST — EKF now flying on LALS/OF only (GPS-DENIED)")
        elif not self.gnss_ok and not self.jam_injected:
            self.gnss_ok = True

    # ---------------------------------------------------------- contacts ---
    def _update_contacts(self, dt: float) -> None:
        # Spawn Edge-AI contacts while the vehicle is airborne and scanning.
        if self.flight_active:
            self.contact_cooldown -= dt
            if self.contact_cooldown <= 0.0:
                self.contact_cooldown = self.rng.uniform(2.5, 6.5) / (1.0 + (self.mode == "NAV"))
                spec = self.rng.choice(THREAT_CLASSES)
                bearing = self.rng.uniform(0.0, 360.0)
                rng_m = self.rng.uniform(18.0, RANGE_LIMIT_M - 10.0)
                conf = self.rng.uniform(0.58, 0.985)
                c = Contact(
                    tid=self.next_contact_id,
                    cls=spec["cls"],
                    priority=spec["priority"],
                    bearing_deg=round(bearing, 1),
                    range_m=round(rng_m, 1),
                    radial_ms=round(self.rng.uniform(-spec["speed"], spec["speed"]), 2),
                    heading_deg=round(self.rng.uniform(0, 360), 0),
                    conf=round(conf, 3),
                    ttl=self.rng.uniform(12.0, 26.0),
                )
                self.next_contact_id += 1
                self.contacts.append(c)
                # Decision matrix per docs: action only when conf > 0.75.
                if conf > 0.75:
                    self._push_log("AI", f"CONTACT #{c.tid} {c.cls} r={c.range_m:.0f}m "
                                         f"brg={c.bearing_deg:03.0f}° conf={c.conf:.2f} "
                                         f"[{c.priority}] → {PRIORITY_ACTION[c.priority]}")
                else:
                    self._push_log("AI", f"CONTACT #{c.tid} {c.cls} conf={c.conf:.2f} — below 0.75 gate, ignored")

        alive: List[Contact] = []
        for c in self.contacts:
            c.step(dt)
            if c.ttl > 0 and c.range_m > 5.0:
                c.bearing_deg = round((c.bearing_deg + self.rng.uniform(-0.6, 0.6)) % 360.0, 1)
                alive.append(c)
            elif c.ttl <= 0:
                self._push_log("AI", f"CONTACT #{c.tid} {c.cls} lost — track expired")
        self.contacts = alive[-14:]

    # ----------------------------------------------------------- snapshot ---
    def snapshot(self) -> Dict[str, Any]:
        x, y, z = self.pos
        vx, vy, vz = self.vel
        return {
            "type": "telemetry",
            "t": round(self.sim_time, 2),
            "tick": self.tick,
            "mode": self.mode,
            "armed": self.armed,
            "flight": self.flight_active,
            "pos": {"x": x, "y": y, "alt": z},
            "vel": {"vx": vx, "vy": vy, "vz": vz, "gs": round(math.hypot(vx, vy), 2)},
            "att": {"yaw": round(self.yaw_deg, 1), "pitch": self.pitch_deg, "roll": self.roll_deg,
                    "throttle": round(self.throttle * 100.0, 1)},
            "batt": {"pct": round(self.batt_pct, 1), "v": self.pack_v, "a": self.current_a},
            "link": {"rssi": self.rssi_dbm, "loss": self.frame_loss_pct},
            "gnss": {"ok": self.gnss_ok, "jam": self.jam_injected},
            "nav": {"source": self.nav_source, "hdop": self.hdop, "err": self.pos_err_m,
                    "est": {"x": self.est_pos[0], "y": self.est_pos[1]}},
            "wpt": {"list": [[round(a, 1), round(b, 1)] for a, b in self.waypoints],
                    "index": self.wpt_index},
            "anchors": [{"name": a.name, "x": a.x, "y": a.y, "z": a.z,
                         "q": round(a.quality, 3), "range": self.anchor_ranges[i] if i < len(self.anchor_ranges) else None}
                        for i, a in enumerate(self.anchors)],
            "contacts": [{"id": c.tid, "cls": c.cls, "prio": c.priority,
                          "brg": c.bearing_deg, "rng": c.range_m, "conf": c.conf,
                          "ttl": round(c.ttl, 1), "radial": c.radial_ms}
                         for c in self.contacts],
            "log": self.log[-60:],
        }
