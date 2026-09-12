# Run with: python3 18_wifi_tcp_socket_server.py
import socket
import time

def start_wifi_telemetry_server():
    print("==================================================================")
    print(" 🦅 BENGAL WINGS :: PYTHON WI-FI TCP TELEMETRY SERVER            ")
    print("==================================================================")

    HOST = '127.0.0.1'  # Localhost / Drone Wi-Fi Access Point IP
    PORT = 5005

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[WI-FI AP]: Server listening on {HOST}:{PORT} (Waiting for GCS link)...")

        # Mocking connection handshake for simulation
        print("[WI-FI LINK]: Client GCS (192.168.1.102) connected successfully!")
        
        for i in range(1, 4):
            telemetry_pkt = f"DRONE_STATUS: ARMED | ALT: {10.5 + i}m | BAT: 96%"
            print(f"[WI-FI TX -> GCS]: {telemetry_pkt}")
            time.sleep(0.4)

        print("[WI-FI LINK]: Session completed gracefully.")

if __name__ == '__main__':
    start_wifi_telemetry_server()