# Run with: python3 06_mavlink_telemetry_parser.py
import struct
import time
import random

def parse_mavlink_attitude_packet(packet_bytes):
    # Simulated Binary Unpacking (Roll, Pitch, Yaw in float32)
    roll, pitch, yaw = struct.unpack('<fff', packet_bytes[0:12])
    return round(roll, 3), round(pitch, 3), round(yaw, 3)

def run_parser_simulation():
    print("==================================================================")
    print(" 🦅 BENGAL WINGS :: PYTHON MAVLINK BINARY TELEMETRY PARSER       ")
    print("==================================================================")

    for i in range(1, 6):
        time.sleep(0.3)
        # Mock binary telemetry payload (3 floats: Roll, Pitch, Yaw)
        mock_payload = struct.pack('<fff', random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(0.0, 360.0))
        roll, pitch, yaw = parse_mavlink_attitude_packet(mock_payload)
        
        print(f"[{time.strftime('%H:%M:%S')}] Packet #{i:03d} -> "
              f"Roll: {roll:>6} rad | Pitch: {pitch:>6} rad | Heading (Yaw): {yaw:>6.1f}°")

if __name__ == '__main__':
    run_parser_simulation()