# ==============================================================================
# 🦅 BENGAL WINGS :: GCS TEST SUITE  (python3 -m unittest discover -s tests)
# ------------------------------------------------------------------------------
# Covers: simulation determinism, flight state machine, LALS trilateration
# math, battery model, command validation, and the RFC 6455 frame codec.
# ==============================================================================
"""Unit tests for the Bengal Wings GCS core (stdlib only, no network)."""

import io
import math
import struct
import unittest

from gcs.server import ws_encode, ws_read_frame, MAX_FRAME
from gcs.sim import BengalWingsSim, trilaterate_2d, TAKEOFF_ALT


def step_n(sim: BengalWingsSim, n: int) -> None:
    for _ in range(n):
        sim.step()


class TestTrilateration(unittest.TestCase):
    """2D trilateration with altitude projection (docs/LALS §1)."""

    def test_recovers_ground_truth_from_perfect_ranges(self):
        anchors = [(-45, 45, 6), (45, 45, 6), (45, -45, 6)]
        px, py, pz = 12.5, -8.25, 25.0
        ranges = [math.dist((px, py, pz), a) for a in anchors]
        got = trilaterate_2d(anchors, ranges, z_ref=pz)
        self.assertIsNotNone(got)
        self.assertAlmostEqual(got[0], px, places=6)
        self.assertAlmostEqual(got[1], py, places=6)

    def test_collinear_anchors_are_rejected(self):
        anchors = [(0, 0, 6), (10, 0, 6), (20, 0, 6)]
        ranges = [100.0, 95.0, 90.0]
        self.assertIsNone(trilaterate_2d(anchors, ranges, z_ref=25.0))

    def test_imaginary_projection_is_rejected(self):
        # slant range shorter than height difference → physically invalid
        anchors = [(0, 0, 6), (40, 0, 6), (0, 40, 6)]
        self.assertIsNone(trilaterate_2d(anchors, [1.0, 1.0, 1.0], z_ref=90.0))


class TestFlightStateMachine(unittest.TestCase):
    def test_takeoff_sequence_reaches_mission_altitude(self):
        sim = BengalWingsSim(seed=7)
        sim.command("arm")
        self.assertEqual(sim.mode, "ARMED")
        sim.command("takeoff")
        self.assertEqual(sim.mode, "TAKEOFF")
        step_n(sim, 240)  # 12 s
        self.assertGreater(sim.pos[2], TAKEOFF_ALT - 3.0)
        self.assertIn(sim.mode, ("NAV", "HOLD"))

    def test_waypoint_capture_and_hold(self):
        sim = BengalWingsSim(seed=11)
        sim.waypoints = [(10.0, 0.0)]
        sim.command("arm"); sim.command("takeoff")
        step_n(sim, 1200)  # 60 s — fly the box corner
        self.assertEqual(sim.mode, "HOLD")
        self.assertEqual(sim.wpt_index, 1)
        self.assertAlmostEqual(sim.pos[0], 10.0, delta=2.0)
        self.assertAlmostEqual(sim.pos[1], 0.0, delta=2.0)

    def test_land_and_autodisarm(self):
        sim = BengalWingsSim(seed=3)
        sim.command("arm"); sim.command("takeoff")
        step_n(sim, 200)
        sim.command("land")
        step_n(sim, 900)  # 45 s descent envelope
        self.assertEqual(sim.mode, "STANDBY")
        self.assertFalse(sim.armed)
        self.assertLess(sim.pos[2], 0.3)

    def test_disarm_denied_while_airborne(self):
        sim = BengalWingsSim(seed=5)
        sim.command("arm"); sim.command("takeoff")
        step_n(sim, 120)
        res = sim.command("disarm")
        self.assertNotEqual(res, "ok")
        self.assertTrue(sim.armed)

    def test_goto_clamped_to_bounds(self):
        sim = BengalWingsSim(seed=2)
        sim.command("goto", x=10_000, y=-99_000)
        x, y = sim.waypoints[-1]
        self.assertLessEqual(abs(x), 161)
        self.assertLessEqual(abs(y), 161)

    def test_unknown_command_returns_error(self):
        sim = BengalWingsSim(seed=1)
        self.assertIn("unknown", sim.command("launch_missiles"))


class TestPowerAndNav(unittest.TestCase):
    def test_battery_drains_monotonically_while_armed(self):
        sim = BengalWingsSim(seed=9)
        sim.command("arm"); sim.command("takeoff")
        pct = sim.batt_pct
        step_n(sim, 600)
        self.assertLess(sim.batt_pct, pct)

    def test_voltage_stays_in_pack_envelope(self):
        sim = BengalWingsSim(seed=9, batt_pct=12.0)
        sim.command("arm"); sim.command("takeoff")
        step_n(sim, 300)
        self.assertGreaterEqual(sim.pack_v, 19.8)
        self.assertLessEqual(sim.pack_v, 25.21)

    def test_jam_denies_gnss_and_flag_switches_nav_log(self):
        sim = BengalWingsSim(seed=4)
        step_n(sim, 100)
        self.assertTrue(sim.gnss_ok)
        sim.command("jam", on=True)
        step_n(sim, 60)
        self.assertFalse(sim.gnss_ok)
        self.assertTrue(sim.jam_injected)
        self.assertIn("LALS", sim.nav_source)
        self.assertTrue(any(l["level"] == "EW" for l in sim.log))
        sim.command("jam", on=False)
        step_n(sim, 60)
        self.assertTrue(sim.gnss_ok)

    def test_lals_position_estimate_tracks_truth(self):
        sim = BengalWingsSim(seed=6)
        sim.command("arm"); sim.command("takeoff")
        step_n(sim, 400)
        err = math.dist(sim.est_pos, (sim.pos[0], sim.pos[1]))
        self.assertLess(err, 3.0, "EKF-lite position estimate must stay bounded")

    def test_determinism_same_seed(self):
        a, b = BengalWingsSim(seed=42), BengalWingsSim(seed=42)
        for _ in range(50):
            a.command("goto", x=30, y=20) if a.tick == 5 else None
            b.command("goto", x=30, y=20) if b.tick == 5 else None
            a.step(); b.step()
        self.assertEqual(a.snapshot(), b.snapshot())


class TestWsCodec(unittest.TestCase):
    """Round-trip the minimal RFC 6455 framing used by the telemetry link."""

    @staticmethod
    def _reader(data: bytes):
        bio = io.BytesIO(data)
        return lambda n: bio.read(n)

    def test_text_frame_roundtrip(self):
        frame = ws_encode('{"cmd":"arm"}')
        op, payload = ws_read_frame(self._reader(frame))
        self.assertEqual(op, 0x1)
        self.assertEqual(payload.decode(), '{"cmd":"arm"}')

    def test_masked_client_frame_roundtrip(self):
        frame = ws_encode("hello masked world", mask=True)
        # client→server frames MUST be masked; reader handles unmasking
        op, payload = ws_read_frame(self._reader(frame))
        self.assertEqual(op, 0x1)
        self.assertEqual(payload.decode(), "hello masked world")
        # confirm masking bit is set on the wire
        self.assertTrue(frame[1] & 0x80)

    def test_16bit_length_branch(self):
        body = "x" * 5000
        frame = ws_encode(body)
        self.assertEqual(struct.unpack(">H", frame[2:4])[0], 5000)
        op, payload = ws_read_frame(self._reader(frame))
        self.assertEqual(len(payload), 5000)

    def test_64bit_length_branch(self):
        # encoder branch test: ≥65536 bytes switches to the 64-bit length form
        body = "y" * 65536
        frame = ws_encode(body)
        self.assertEqual(frame[1] & 0x7F, 127)
        self.assertEqual(struct.unpack(">Q", frame[2:10])[0], 65536)

    def test_16bit_branch_for_smallish_payloads(self):
        frame = ws_encode("z" * (MAX_FRAME - 1))
        self.assertEqual(frame[1] & 0x7F, 126)
        self.assertEqual(struct.unpack(">H", frame[2:4])[0], MAX_FRAME - 1)

    def test_close_and_ping_opcodes(self):
        for code in (0x8, 0x9):
            op, _ = ws_read_frame(self._reader(ws_encode("", opcode=code)))
            self.assertEqual(op, code)

    def test_oversized_frame_rejected(self):
        bad = struct.pack(">BBQ", 0x81, 127, MAX_FRAME + 1)
        with self.assertRaises(ValueError):
            ws_read_frame(self._reader(bad))

    def test_clean_eof_returns_none(self):
        self.assertIsNone(ws_read_frame(self._reader(b"")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
