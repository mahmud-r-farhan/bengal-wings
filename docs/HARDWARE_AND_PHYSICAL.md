# 🛠 Physical Systems, Propulsion & Airframe Engineering

> **System Component:** Aegis-Core Drone Assembly  
> **Document Version:** 1.0.0 (Phase 1 Baseline)  
> **Target Operation Environment:** GPS-Denied / Jammed Electronic Warfare Zones  

---

## 📑 Executive Summary

এই নথিতে **Bengal Wings** অটোনোমাস ড্রোনের ভৌত উপাদান (Airframe), মোটর ও প্রোপালশন সিস্টেম (Propulsion), অন-বোর্ড চিপসেট (Companion Computer & Flight Controller) এবং পাওয়ার ডিস্ট্রিবিউশনের ইলেকট্রিক্যাল ও মেকানিক্যাল ডিজাইন বিশদভাবে ব্যাখ্যা করা হয়েছে।

---

## 🏋️ 1. Physical Specifications & Payload Weight Budget

অটোনোমাস মিশন পরিচালনার জন্য ড্রোনে অতিরিক্ত প্রসেসিং ইউনিট (Edge AI Engine) এবং দূরত্ব মাপার সেন্সর যুক্ত করা হয়। ফলে অতিরিক্ত ওজনের কারণে ড্রোনের ফ্লাইং টাইম যেন মারাত্মকভাবে না কমে, তাই প্রতিটি উপাদানের ওজন গ্রাম (Gram) হিসেবে হিসেব করা বাধ্যতামূলক।

* **Airframe Standard:** 7-Inch Arm Tactical Quadcopter Frame (3K Carbon Fiber Matte Finish).
* **Frame Wheelbase:** 320mm to 350mm Diagonal (Custom Vibration Isolation Dampeners).
* **Target Take-Off Weight (AUW):** 1650g – 1850g.
* **Maximum Payload Capacity:** 650g.
* **Estimated Hover Time:** 18 – 24 Minutes (6S 4500mAh 21700 High-Drain Li-ion Pack).

### Bill of Materials (BOM) & Weight Matrix

| Category | Component Description | Quantity | Unit Weight | Total Weight | Status |
|---|---|---|---|---|---|
| **Structure** | 7-inch Carbon Fiber Tactical Frame | 1 | 220 g | 220 g | Selected |
| **Propulsion** | Brushless Motor 2806.5 1300KV | 4 | 60 g | 240 g | Selected |
| **Propulsion** | 7x4x3 Polycarbonate Propeller Pairs | 2 | 18 g | 36 g | Selected |
| **Power ESC** | 4-in-1 55A BLHeli_32 / AM32 ESC | 1 | 25 g | 25 g | Selected |
| **Flight FC** | Holybro Pixhawk 6C / FMUv5 Standard | 1 | 45 g | 45 g | Selected |
| **Companion Processing**| NVIDIA Jetson Orin Nano (Bareboard + Custom Heatsink)| 1 | 135 g | 135 g | Selected |
| **Cameras** | Stereo Vision Unit (RealSense D435i / ZED Mini) | 1 | 90 g | 90 g | Selected |
| **Sensors** | Benewake TFmini Plus LiDAR Rangefinder | 1 | 15 g | 15 g | Selected |
| **Sensors** | Optical Flow Sensor Module (PMW3901) | 1 | 12 g | 12 g | Selected |
| **Telemetry Radio** | ExpressLRS 900MHz / Microhard Radio Node | 1 | 35 g | 35 g | Selected |
| **Positioning** | LALS UWB Rover Module (DWM3000 Custom PCB) | 1 | 28 g | 28 g | Prototype |
| **Battery** | 6S1P 21700 Li-ion 4500mAh High-Drain Cell Pack | 1 | 680 g | 680 g | Custom Built |
| **Miscellaneous** | Cables, Connectors, Standoffs, TPU 3D Mounts | 1 Set | 80 g | 80 g | Assembly |
| **TOTAL AUW** | | | | **1641 grams** | **Balanced** |

---

## ⚡ 2. Electrical Power Architecture & Wiring Schematic

ড্রেনটি সম্পূর্ণ ব্যাটারির ২২.২V থেকে ২৪V ডায়রেক্ট পাওয়ার দিয়ে চলে। কিন্তু বিভিন্ন স্পিডের প্রসেসর এবং সেন্সরের জন্য আলাদা আলাদা স্টেবিলাইজড ভোল্টেজ ব্যাক বোন প্রয়োজন।


```

```
                           ┌───────────────────────────────┐
                           │  6S Li-ion Battery Pack       │
                           │  (22.2V Nominal - 25.2V Max)  │
                           └───────────────┬───────────────┘
                                           │ XT60 Connection
                                           ▼
                           ┌───────────────────────────────┐
                           │ Power Distribution Board (PDB)│
                           └───────┬───────────────┬───────┘
                                   │               │
          ┌────────────────────────┘               └────────────────────────┐
          │ Direct Battery Voltage (22.2V)                                  │ 12V Buck Converter (5A Peak)
          ▼                                                                 ▼

```

┌───────────────────────┐                                         ┌───────────────────────┐
│ 4-in-1 55A ESC        │                                         │ NVIDIA Jetson Orin    │
│ (Motor Driver)        │                                         │ Companion Computer    │
└───────────┬───────────┘                                         └───────────┬───────────┘
│ PWM / DShot Signals                                             │ USB 3.0 / UART
▼                                                                 ▼
┌───────────────────────┐  MAVLink Telemetry (UART)               ┌───────────────────────┐
│ Flight Controller     │◄───────────────────────────────────────►│ Stereo Camera, LiDAR  │
│ (Pixhawk 6C - 5V BEC) │                                         │ & LALS UWB Module     │
└───────────────────────┘                                         └───────────────────────┘

```

### Voltage Regulation Breakdown:
1. **ESC & Motors:** Direct 6S Li-ion Voltage (22.2V - 25.2V).
2. **NVIDIA Jetson Orin Nano:** Regulated 12V DC via High-Efficiency DC-to-DC Buck Converter (Minimum 5A peak support).
3. **Flight Controller & Telemetry:** Regulated 5.2V DC from Power Module.
4. **Sensors (Optical Flow, LiDAR, LALS):** 5V / 3.3V Logic Level from Companion & Flight Controller Ports.

---

## 🎛 3. On-Board Processing & Sensor Mounting Layout

### Mechanical Placement Layout (Center of Gravity Optimization)


```

```
    ┌────────────────────────────────────────────────────────┐
    │ Top Plate: NVIDIA Jetson Orin Nano + Heatsink & Fan   │
    ├────────────────────────────────────────────────────────┤
    │ Middle Stack: Pixhawk 6C FCU (On Vibration Dampeners)   │
    ├────────────────────────────────────────────────────────┤
    │ Bottom Deck: Downward Optical Flow + LiDAR Rangefinder │
    └────────────────────────────────────────────────────────┘
                               ▲
                               │
                   LALS UWB Tag Mounted on 
                   Front/Rear Standoff

```

```
