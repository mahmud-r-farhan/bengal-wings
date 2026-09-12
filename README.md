# 🦅 Bengal Wings (`bengal-wings`)

> **Autonomous Aerial Reconnaissance, Edge AI & Defence Ecosystem**
> 
>   
> 
> _Architected for GPS-Denied Warfare, Local Area Positioning Systems (LALS), Autonomous Swarm Orchestration, and Counter-UAV Defense._
> 
>   

## 📄 Executive Summary & Vision

**Bengal Wings** হলো একটি প্রোডাকশন-গ্রেড, মডিউলার এবং ডিফেন্স-ফার্স্ট অটোনোমাস রোবোটিক ইকোসিস্টেম। ২০২৬ সালের ইলেকট্রনিক ওয়ারফেয়ার (EW), জিপিএস জ্যামিং, এবং স্যাটেলাইট বিচ্ছিন্ন (GPS-Denied) যুদ্ধক্ষেত্রের চ্যালেঞ্জ মোকাবিলায় এটি ডিজাইন করা হয়েছে।

  

এই রিপোজিটরি হল সিস্টেমের একক ডিজিটাল কারখানাস্বরূপ (Single Source of Truth)। এখানে সিস্টেমের চূড়ান্ত ভিশন—যা ভবিষ্যতে ৭টি মূল প্রতিরক্ষা মডিউল কভার করবে—এবং বর্তমানের প্রথমিক বাস্তবায়ন পর্ব (Phase 1) একই সাথে বিন্যস্ত করা হয়েছে।

  

## 📂 Repository Directory Tree

রিপোজিটরির সম্পূর্ণ স্ট্রাকচারটি নিচে তুলে ধরা হলো। পরবর্তী ফাইলগুলো এই ফোল্ডার স্ট্রাকচার অনুসারেই বিন্যস্ত:

  

```
bengal-wings/
├── README.md                          # Global Master Architecture & Roadmap
├── LICENSE                            # Software & Hardware Licensing Rules
├── docs/
│   ├── HARDWARE_AND_PHYSICAL.md       # Drone Frame, Flight Controller & Sensors
│   ├── SOFTWARE_AND_FIRMWARE.md       # PX4, ROS2, Visual SLAM & GCS Architecture
│   ├── AI_AND_THREAT_DETECTION.md     # TensorRT, YOLOv10 & Sensor Fusion
│   ├── LALS_MANUFACTURING_AND_TEST.md # Local Area Positioning System (UWB) Specs & Tests
│   └── FUTURE_MODULES_ARCH.md         # Architecture for Swarms, UGV, Anti-Drone & CQB Micro-UAVs

```

## 🗺️ Master System Architecture

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

## 🚀 Production Phase & Roadmap

### Phase 1: Foundation (Active Phase)

-   [x] GPS-Denied Indoor/Outdoor Visual Navigation (Optical Flow + Visual SLAM).
    
      
    
-   [x] Edge Computing Threat Detection Pipeline (YOLOv10 + NVIDIA TensorRT).
    
      
    
-   [x] **LALS (Local Area Positioning System)** Anchor & Rover Module R&D.
    
      
    
-   [x] Telemetry Stream and Ground Control Station (GCS) Core.
    
      
    

### Phase 2: Mesh & Swarm Readiness

-   [ ] Encrypted P2P Tactical Mesh Communication Node.
    
      
    
-   [ ] Anti-tamper Hardware Self-Destruct / Data-Wipe Mechanism.
    
      
    
-   [ ] Multi-drone Swarm Coordination Protocol.
    
      
    

### Phase 3: Land & Air Hybrid Systems

-   [ ] Unmanned Ground Vehicle (UGV) Base Unit integration with Drone Docking.
    
      
    
-   [ ] Micro-UAV Deployment Mechanism for CQB / Indoor Reconnaissance.
    
      
    

### Phase 4: Active Electronic & Kinetic Defence

-   [ ] Counter-UAV Jamming Module & Autonomous Interceptor Drone.
    
      
    