# 🦅 Bengal Wings :: Playground & Examples

Welcome to the **Bengal Wings Playground**! This directory contains a comprehensive suite of **25 standalone code examples** demonstrating various layers of the drone ecosystem—from low-level PCB firmware and bare-metal drivers to high-level GCS apps, AI pipelines, wireless protocols, and system automation scripts.

---

## 📂 Directory Structure & Module Index

```text
bengal-wings/
├── playground/
│   ├── 01_flight_telemetry_sim.rs          # [Rust] Terminal Flight Telemetry Simulator (waypoint mission + LALS coords)
│   ├── 02_ai_threat_detector.py            # [Python] Edge-AI Threat Feed Monitor (YOLOv10-style)
│   ├── 03_lals_mesh_server.go              # [Go] LALS UWB Anchor Mesh & Trilateration Server
│   ├── 04_radar_tactical_dashboard.html    # [HTML5/Canvas] Radar HUD with click-to-waypoint
│   ├── 05_px4_mavlink_bridge.cpp           # [C++] PX4 ↔ MAVLink Sensor Bridge
│   ├── 06_mavlink_telemetry_parser.py      # [Python] Binary MAVLink Attitude Packet Parser
│   ├── 07_gcs_websocket_bridge.ts          # [TypeScript] Node.js Real-time GCS Event Bus
│   ├── 08_mission_planner_sim.cs           # [C#] Tactical Waypoint Mission Engine (.NET)
│   ├── 09_low_level_memory_allocator.zig   # [Zig] Low-Latency Sensor Ring Buffer
│   ├── 10_auto_system_diagnostics.sh       # [Shell/Bash] On-Board System Health Audit
│   ├── 11_android_gcs_controller.kt        # [Kotlin] Mobile GCS Ground Link Controller
│   ├── 12_ros2_drone_telemetry_node.cpp    # [ROS 2 / C++] Autonomous Drone Control Node
│   ├── 13_raspberry_pi_gpio_sensors.py     # [Raspberry Pi] GPIO LiDAR & Ultrasonic Reader
│   ├── 14_stm32_firmware_freertos.cpp      # [PCB / STM32] Embedded FreeRTOS Control Tasks
│   ├── 15_esp32_espnow_mesh_network.ino    # [ESP32 / Arduino C++] Swarm Mesh Network (ESP-NOW)
│   ├── 16_kinematics_quadcopter_motors.py  # [Robotics Math] Motor PWM Kinematics Mixer
│   ├── 17_pcb_i2c_sensor_driver.c          # [Bare-Metal C] Barometer Register-Level Driver
│   ├── 18_wifi_tcp_socket_server.py        # [Python] Wi-Fi TCP Telemetry Socket Server
│   ├── 19_ble_gatt_server_embedded.cpp     # [ESP32 / C++] BLE Wireless GATT Configuration
│   ├── 20_udp_broadcast_ground_link.go     # [Go] High-Speed UDP Video & Data Streaming
│   ├── 21_lora_sx1276_spi_driver.c         # [PCB / C] LoRa 868/915 MHz Sub-GHz Radio Driver
│   ├── 22_mqtt_gcs_cloud_publisher.ts      # [TypeScript] 4G/LTE Cloud MQTT Telemetry Bridge
│   ├── 23_zeromq_drone_mesh_bus.rs         # [Rust] ZeroMQ Low-Latency Peer-to-Peer Bus
│   ├── 24_system_setup_and_deploy.sh       # [Bash] System Dependency & Deployment Manager
│   ├── 25_bengal_wings_daemon.service      # [Linux Systemd] Background Daemon Auto-Start Config
│   ├── Makefile                            # Playground shortcut runner (run from playground/)
│   └── README.md                           # This index
└── gcs/                                    # ➡ The PRODUCTION Phase-1 GCS Core lives at ../gcs

```

---

## 🛠️ Category Breakdown

| Category | Files | Languages / Tools | Core Purpose |
| --- | --- | --- | --- |
| **Core Flight Logic** | `01` - `05` | Rust, Python, Go, HTML, C++ | Terminal telemetry sim, threat feed, LALS trilateration mesh, radar HUD, PX4 bridge. |
| **GCS & Higher Level API** | `06` - `11` | Python, TS, C#, Zig, Bash, Kotlin | WebSockets, mobile ground control app, mission planning, telemetry parsing. |
| **Robotics & Firmware** | `12` - `17` | ROS 2, RPi, STM32, ESP32, Math, C | FreeRTOS tasks, motor PWM kinematics, ROS 2 nodes, bare-metal I2C register drivers. |
| **Wireless Protocols** | `18` - `23` | Python, C++, Go, C, TS, Rust | Wi-Fi TCP, BLE GATT, UDP streaming, LoRa long-range, MQTT cellular, ZeroMQ mesh. |
| **System & Automation** | `24` - `25` | Bash, Linux Systemd | Setup automation, dependency auditing, background boot daemon service. |

---

## 🚀 How to Run Examples

> Every file also carries its own one-line `# Run with:` command in its header.

### 1. Rust

```bash
rustc -O playground/01_flight_telemetry_sim.rs && ./01_flight_telemetry_sim   # needs rustc
```

### 2. Python Scripts

```bash
python3 playground/02_ai_threat_detector.py
python3 playground/06_mavlink_telemetry_parser.py
python3 playground/18_wifi_tcp_socket_server.py

```

### 3. C / C++ Files (GCC / Clang)

```bash
# Compile and run bare-metal driver (host smoke-build works — register map is stubbed)
gcc -O2 playground/17_pcb_i2c_sensor_driver.c -o i2c_driver && ./i2c_driver

# Compile LoRa driver
gcc -O2 playground/21_lora_sx1276_spi_driver.c -o lora_driver && ./lora_driver

```

### 4. Go Modules

```bash
go run playground/03_lals_mesh_server.go
go run playground/20_udp_broadcast_ground_link.go

```

### 5. TypeScript / Node.js

```bash
npx ts-node playground/07_gcs_websocket_bridge.ts
npx ts-node playground/22_mqtt_gcs_cloud_publisher.ts

```

### 6. HTML (No Toolchain)

```bash
xdg-open playground/04_radar_tactical_dashboard.html      # any browser
```

### 7. Bash & Automation Scripts

```bash
bash playground/10_auto_system_diagnostics.sh
bash playground/24_system_setup_and_deploy.sh   # targets Jetson/Ubuntu hosts
```

> ⭐ **No toolchain handy?** Skip straight to the flagship: `make gcs` from the
> repo root runs the full Phase-1 GCS core (Python stdlib only) at
> http://localhost:8090/.

---

## 📋 System Requirements

* **Languages:** Python 3.9+, Go 1.20+, Node.js 18+, GCC/G++ 11+, Rust/Cargo, Zig 0.11+
* **Embedded Targets:** STM32 MCU, ESP32, Raspberry Pi 4/5, Jetson Nano/Orin
* **Operating Systems:** Linux (Ubuntu 22.04 LTS / Debian / Raspbian recommended)

---

> 💡 **Tip:** Use the **repo-root `Makefile`** shortcuts (`make gcs`, `make test`,
> `make check`) for the flagship GCS core, or run `make help` from inside
> `playground/` for the example-only targets.
