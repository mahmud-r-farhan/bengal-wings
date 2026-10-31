# 🦅 Bengal Wings (`bengal-wings`)

> **Aerial-systems simulation & community emergency-response tools**
>
> _An experimental software repository: a deterministic GCS simulator and Shomoy (সময়), an offline-capable local flood-response board. No live aircraft, sensors, or dispatch service._
> 
>   

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Hardware: CERN-OHL-S-v2](https://img.shields.io/badge/HW%20License-CERN--OHL--S--v2-orange.svg)](LICENSE)
[![CI](https://github.com/mahmud-r-farhan/bengal-wings/actions/workflows/ci.yml/badge.svg)](https://github.com/mahmud-r-farhan/bengal-wings/actions/workflows/ci.yml)
[![Python 3.9+ stdlib-only](https://img.shields.io/badge/Python-3.9%2B%20stdlib--only-3776ab)](gcs/)

## ⚡ Quick Start — Try It in 60 Seconds

রিপোজিটরির Phase 1 **GCS Core** এখন সম্পূর্ণ কার্যকর — কোনো ডিপেন্ডেন্সি ছাড়াই, শুধুমাত্র Python standard library:

```bash
git clone https://github.com/mahmud-r-farhan/bengal-wings.git
cd bengal-wings
make gcs          # → খুলুন: http://localhost:8090/
make test         # ২২টি unit tests: flight model, LALS trilateration, WS codec
```

The GCS simulation console includes radar, simulated LALS telemetry and mission controls. **Simulated data only — no live aircraft or hardware is connected or controlled.**

### Community response board

Open **[http://localhost:8090/response.html](http://localhost:8090/response.html)** for Shomoy (সময়), an offline-capable flood/community response board. It lets local volunteers record and prioritize needs, keep follow-up status, register nearby capacity (boats, teams, shelter, water), and export/import JSON backups or CSV reports. It uses browser-local storage only; there are no accounts, network uploads, or third-party map/font dependencies. Install the page once while online to cache the app shell for offline use. GPS is optional, permission-based and stays on the device.

This is a coordination aid—not an official warning, needs assessment, dispatch system, or substitute for Bangladesh's local disaster-management authorities. Verify reports and coordinate urgent action with responsible local responders. See [GCS docs](gcs/README.md#community-response-board) for privacy, backup, and operating notes.

---

## 📄 Executive Summary & Vision

**Bengal Wings is an experimental software repository—not a production drone system.** Its runnable aerial component is a deterministic, simulated Ground Control Station (GCS); no hardware, real navigation, object detection, or aircraft control is implemented or validated here. The hardware, firmware and autonomy documents are design notes, not field-tested specifications.

The repository now also includes **Shomoy (সময়)**, a practical, offline-capable community flood-response board for recording needs and nearby resources. It stores records in one browser only and does not send alerts, dispatch help, or sync between devices. Use it with local authorities, verify every report, and export backups carefully. See [GCS documentation](gcs/README.md#community-response-board) for details.

  

## 📂 Repository Directory Tree

রিপোজিটরির সম্পূর্ণ স্ট্রাকচারটি নিচে তুলে ধরা হলো। পরবর্তী ফাইলগুলো এই ফোল্ডার স্ট্রাকচার অনুসারেই বিন্যস্ত:

  

```
bengal-wings/
├── README.md                          # Global Master Architecture & Roadmap (this file)
├── Makefile                           # Repo shortcuts: make gcs | make test | make check
├── LICENSE                            # Software (GPLv3) & Hardware (CERN-OHL-S-v2) Licensing Rules
├── .github/workflows/ci.yml           # CI gate: syntax, unit tests, GCS boot smoke test
├── docs/
│   ├── HARDWARE_AND_PHYSICAL.md       # Drone Frame, Flight Controller & Sensors
│   ├── SOFTWARE_AND_FIRMWARE.md       # PX4, ROS2, Visual SLAM & GCS Architecture
│   ├── AI_AND_THREAT_DETECTION.md     # TensorRT, YOLOv10 & Sensor Fusion
│   ├── LALS_MANUFACTURING_AND_TEST.md # Local Area Positioning System (UWB) Specs & Tests
│   └── FUTURE_MODULES_ARCH.md         # Architecture for Swarms, UGV, Anti-Drone & CQB Micro-UAVs
├── gcs/                               # ⭐ Phase 1 GCS CORE — runnable telemetry server + dashboard
│   ├── sim.py                         #   Flight / LALS / Edge-AI / power simulation engine
│   ├── server.py                      #   HTTP + RFC 6455 WebSocket stream (stdlib only)
│   └── web/                           #   Simulator UI + Shomoy response board (HTML/CSS/JS)
├── playground/                        # 25 standalone cross-layer code examples (see its README)
├── tasks/
│   ├── PHASE_01_STARTER_PLAN.md       # Step-by-step Phase 1 execution plan
│   └── SCRATCH_BUILD_TASK_PLAN.md     # End-to-end scratch build pipeline plan
└── tests/
    └── test_gcs.py                    # GCS core unit suite (python3 -m unittest)
```

## 🗺️ Concept architecture (not implemented)

The block diagram below is aspirational documentation only; only the simulator and browser-based response board run in this repository. It is not evidence of tested airframe, perception, navigation or communications capability.

```
                                 ┌──────────────────────────────────────────┐
                                 │ Ground Control Station (GCS) Dashboard   │
                                 │   (Flutter / React Desktop + WebSockets) │
                                 └────────────────────▲─────────────────────┘
                                                      │ Encrypted Radio / P2P Mesh
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       AEGIS-CORE DRONE SYSTEM                                          │
│                                                                                                        │
│  ┌──────────────────────────────┐        MAVLink        ┌───────────────────────────────────────────┐  │
│  │ Flight Controller Unit (FCU) │◄─────────────────────►│ Edge Companion Computer                   │  │
│  │  - PX4 Autopilot Firmware    │  (Micro-XRCE-DDS)     │  - NVIDIA Jetson Orin Nano (8GB VRAM)     │  │
│  │  - EKF3 Navigation Filter    │                       │  - ROS 2 Humble/Jazzy Middleware          │  │
│  └──────────────▲───────────────┘                       └─────────────────────▲─────────────────────┘  │
│                 │ Sensor Signals                                              │ Camera / RF Data       │
│  ┌──────────────┴───────────────┐                       ┌─────────────────────┴─────────────────────┐  │
│  │ Onboard Sensors              │                       │ Vision & Positioning Hardware             │  │
│  │  - Optical Flow + LiDAR      │                       │  - Stereo Camera (RealSense/ZED)          │  │
│  │  - IMU & Barometer           │                       │  - LALS UWB Rover Module (DWM3000)        │  │
│  └──────────────────────────────┘                       └───────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                      ▲
                                                      │ Radio Time-of-Flight (ToF)
                                                      ▼
                                 ┌──────────────────────────────────────────┐
                                 │ LALS Ground Anchor Network               │
                                 │  - 3x to 4x UWB Beacons on High Poles    │
                                 └──────────────────────────────────────────┘

```

## 🚀 Development roadmap (prototype scope)

### Current, runnable software

-   [x] Deterministic GCS flight / LALS / perception / power **simulation** — [`gcs/`](gcs/). Simulated contacts and injected GNSS degradation are not real sensor detections or RF testing.
-   [x] Shomoy community flood-response board — offline shell, local-browser storage, needs follow-up, local resource register and export/import.

### Next useful steps for Shomoy (not yet implemented)

-   [ ] Review the forms and triage labels with Bangladesh community responders before operational use.
-   [ ] Add a complete Bangla interface and test it with low-bandwidth, low-literacy workflows.
-   [ ] Design a safe handoff workflow for multiple devices; there is no shared database or synchronization today.
-   [ ] Only publish verified shelter/contact directories with a named maintainer and a visible last-checked date; none are bundled because stale emergency information can be dangerous.

The aerial hardware, autonomy, and networking concepts elsewhere in `docs/` remain **unimplemented research notes**, not committed production phases or field-tested capabilities.