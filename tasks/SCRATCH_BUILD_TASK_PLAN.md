# 🚁 Task Plan: Building a Flying Autonomous Reconnaissance Drone from Scratch

> **Project Target:** Design, assemble, calibrate, and program a high-performance 7-inch Autonomous Drone.  
> **Primary Goal:** Take off, hover, navigate, and execute AI tasks safely in real-world environments.  
> **Version:** 1.0.0 Baseline Plan  

---

## 🗺️ Master Project Roadmap


```

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                SCRATCH DRONE BUILD PIPELINE                              │
├─────────────────┬──────────────────┬──────────────────┬────────────────┬────────────────┤
│ PHASE 1: BOM    │ PHASE 2: HARDWARE│ PHASE 3: FIRMWARE│ PHASE 4: FIRST │ PHASE 5: AI &  │
│ & PROCUREMENT   │ ASSEMBLY & WIRING│ & CALIBRATION    │ FLIGHT TEST    │ AUTONOMY       │
└─────────────────┴──────────────────┴──────────────────┴────────────────┴────────────────┘

```

---

## 📦 Phase 1: Hardware Selection & Procurement (BOM)

প্রথমেই সঠিক যন্ত্রাংশ পছন্দ করা জরুরি যাতে মোটর, ইলেকট্রনিক্স এবং ব্যাটারির ওজনের ভারসাম্য (Thrust-to-Weight Ratio) অন্তত **২.৫:১** থাকে।

### Required Components Breakdown:
* **Airframe:** 7-Inch Arm 3K Carbon Fiber Quadcopter Frame (Wheelbase ~330mm).
* **Motors:** 4x Brushless Motors (2806.5 Size, 1300KV to 1500KV).
* **Propellers:** 4x Polycarbonate Propellers (7x4x3 Pitch).
* **ESC (Electronic Speed Controller):** 4-in-1 50A - 60A BLHeli_32 or AM32 ESC.
* **Flight Controller (FC):** Holybro Pixhawk 6C / Pixhawk 4 (or Matek H743 for smaller setups).
* **Companion Computer:** NVIDIA Jetson Orin Nano (8GB VRAM) or Raspberry Pi 4/5.
* **Sensors:**
  * Downward Optical Flow Sensor (PMW3901).
  * Downward LiDAR Rangefinder (TFmini Plus / Benewake).
  * Forward Stereo Camera (Intel RealSense D435i).
* **Telemetry & Radio:** ExpressLRS (ELRS) 900MHz Receiver & Transceiver.
* **Battery:** 6S1P 4500mAh 21700 High-Drain Li-ion Pack (or 6S 3000mAh Lipo 120C).
* **Power Hardware:** XT60 Connector, 12V 5A Buck Converter (For Jetson), Silicon Wires (12AWG & 20AWG), Heat Shrink Tubes.

---

## 🛠️ Phase 2: Physical Hardware Assembly & Wiring

### Step 2.1: Frame & Motor Mounting
1. কার্বন ফাইবার ফ্রেমের বেস প্লেটের সাথে ৪টি আর্ম সঠিকভাবে নাট-বোল্ট দিয়ে শক্ত করে লাগান।
2. ফ্রেমের চার কোণায় ৪টি ব্রাশলেস মোটর মাউন্ট করুন। 
   * **Important:** মোটরের স্ক্রু যেন মোটরের ভেতরের তামার কুণ্ডলী (Coil)-তে স্পর্শ না করে।

### Step 2.2: Soldering Power Architecture (PDB & ESC)
1. 4-in-1 ESC-এর পাওয়ার প্যাডে ব্যাটারির মূল XT60 ক্যাবল (12AWG Wire) সোল্ডার (Solder) করুন।
2. ৪টি মোটরের প্রতিটির ৩টি করে তার 4-in-1 ESC-এর নির্দিষ্ট ৩টি প্যাডে সোল্ডার করুন।
3. **Buck Converter Integration:** ESC-এর মেইন পাওয়ার প্যাড থেকে একটি 12V Buck Converter সংযোগ করুন যা পরে NVIDIA Jetson Orin Nano-তে পাওয়ার দেবে।

### Step 2.3: Mounting Flight Controller & Companion Unit
1. **Pixhawk FC Setup:** ফ্রেমের ঠিক মধ্যভাগে (Center of Gravity) ৪টি এন্টি-ভাইব্রেশন রাবার ড্যাম্পেনারের ওপর Pixhawk ফ্লাইট কন্ট্রোলার বসান (তীরের চিহ্ন যেন ড্রোনের সামনের দিকে থাকে)।
2. **Sensors Setup:** 
   * ড্রোনের নিচে Optical Flow এবং LiDAR রিডিং নেওয়ার জন্য পারপেন্ডিকুলার (৯০ ডিগ্রি) মাউন্ট বসান।
   * ড্রোনের ওপরের প্লেটে NVIDIA Jetson Orin Nano এবং অ্যাক্টিভ ফ্যান মাউন্ট করুন।

---

## 🕹️ Phase 3: Firmware Flashing & Ground Calibration

### Step 3.1: PX4 Autopilot Firmware Installation
1. কম্পিউটারে **QGroundControl (QGC)** সফটওয়্যার ইনস্টল করুন।
2. USB-C ক্যাবল দিয়ে Pixhawk-কে পিসির সাথে কানেক্ট করুন।
3. QGroundControl-এর **Firmware** সেকশনে গিয়ে **PX4 Autopilot (v1.14+)** সিলেক্ট করে ফ্ল্যাশ করুন।

### Step 3.2: Sensor Calibration
QGC ইন্টারফেস থেকে একে একে নিচের ড্রাইভার ও সেন্সর ক্যালিব্রেশন সম্পন্ন করুন:
* **Frame Selection:** Generic 7" Quadcopter Frame সিলেক্ট করুন।
* **Sensor Calibration:** 
  * **Accel & Gyro:** ড্রোনটিকে নির্দেশনামতো ৬টি ভিন্ন দিকে ঘুরিয়ে এক্সেলোমিটার ক্যালিব্রেট করুন।
  * **Compass:** ড্রোনটিকে ৩৬০ ডিগ্রিতে ঘুরিয়ে কম্পাস সেট করুন।
  * **Radio & ESC Calibration:** রেডিও রিমোটের স্টিক সীমানা এবং ESC-এর থ্রোটল রেঞ্জ ম্যাচ করুন।

---

## 🛫 Phase 4: Maiden Flight Test (Manual & Hover Check)

ড্রোন প্রথমবার উড্ডয়নের পূর্বে ডাবল চেক এবং টেস্ট ফ্লাইটের ধাপ:

1. **Pre-Flight Inspection Check:**
   * সব নাট-বোল্ট টাইট আছে কিনা এবং ড্রোনের সেন্টার অফ গ্র্যাভিটি (CG) ব্যালেন্সড কিনা।
   * **Propeller Direction Check:** ঘড়ির কাঁটার দিকে (CW) এবং বিপরীতে (CCW) মোটর ঠিকভাবে ঘুরছে কিনা নিশ্চিত না হয়ে প্রোপেলার লাগাবেন না!
2. **Propeller Installation:** মেইন মোটর ডিরেকশন কনফার্ম করে প্রোপেলারগুলো মোটর শ্যাফটে টাইট করে লাগান।
3. **Bench Test (No Props):** প্রোপেলার ছাড়া ব্যাটারি প্লাগইন করে আর্ম (Arm) করুন এবং রেডিও রিমোট দিয়ে থ্রোটল বাড়িয়ে প্রসেস দেখুন।
4. **First Manual Flight (Stabilized Mode):**
   * ড্রোনটিকে একটি ফাঁকা খোলা মাঠে নিয়ে যান।
   * **Stabilize Mode** অথবা **Altitude Hold Mode** বেছে নিন।
   * ড্রোন আর্ম করে আস্তে আস্তে থ্রোটল দিন এবং মাটি থেকে ১-২ মিটার ওপরে টেক-অফ করে স্টেবল হোল্ড চেক করুন।

---

## 🧠 Phase 5: Autonomous Navigation & AI Integration

ড্রোন ম্যানুয়ালি সঠিকভাবে উড়তে সক্ষম হলে সেটিতে স্বায়ত্তশাসন যুক্ত করার ধাপ:

### Step 5.1: Companion Computer Connectivity
1. Pixhawk-এর `TELEM2` পোর্ট থেকে Jetson-এর `UART (/dev/ttyTHS1)` পোর্টে MAVLink তার যুক্ত করুন।
2. Jetson-এ **ROS 2** এবং **Micro-XRCE-DDS Agent** রান করে ফ্লাইট কন্ট্রোলারের সাথে বাই-ডিরেকশনাল কানেক্টিভিটি চালু করুন:
   ```bash
   MicroXRCEAgent serial --dev /dev/ttyTHS1 -b 921600

```

### Step 5.2: GPS-Denied Position Estimator (EKF2)

QGroundControl থেকে সেন্সর কম্বিনেশন এনাবল করুন:

* `EKF2_GPS_CTRL = 0` (জিপিএস বন্ধ)
* `EKF2_EV_CTRL = 15` (Optical Flow + Stereo Camera Vision-এর মাধ্যমে পজিশন কন্ট্রোল)
* `EKF2_HGT_MODE = 2` (LiDAR দিয়ে গ্রাউন্ড ডিস্ট্যান্স হিসাব করা)

### Step 5.3: Autonomous Mission Script (`takeoff_and_hover.py`)

ROS 2 নোডের মাধ্যমে ড্রোনকে নিজের সিদ্ধান্ত নিয়ে উড়ার প্রথম পাইলট টেস্ট ফাইল:

```python
import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand

class AutonomousTakeoffNode(Node):
    def __init__(self):
        super().__init__('autonomous_takeoff_node')
        self.publisher_mode = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.publisher_trajectory = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.publisher_cmd = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)
        
        self.timer = self.create_timer(0.1, self.cmd_loop)
        self.counter = 0

    def cmd_loop(self):
        # Publish Offboard Heartbeat
        offboard_msg = OffboardControlMode()
        offboard_msg.position = True
        offboard_msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_mode.publish(offboard_msg)

        # Target Takeoff Position (2.0 meters high)
        trajectory = TrajectorySetpoint()
        trajectory.position = [0.0, 0.0, -2.0] # NED Frame (Negative Z is UP)
        trajectory.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_trajectory.publish(trajectory)

        # Arm and Set Offboard Mode after 1 second
        if self.counter == 10:
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0) # Offboard
            self.send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0) # Arm
        
        self.counter += 1

    def send_vehicle_command(self, command, param1=0.0, param2=0.0):
        cmd = VehicleCommand()
        cmd.command = command
        cmd.param1 = param1
        cmd.param2 = param2
        cmd.target_system = 1
        cmd.target_component = 1
        cmd.from_external = True
        cmd.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_cmd.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = AutonomousTakeoffNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

```

---

## 📋 Task Checklist Summary

* [ ] **Procurement:** সব হার্ডওয়্যার, মোটর, পিক্সহক ও জেটসন পার্টস সংগ্রহ করা।
* [ ] **Assembly:** ফ্রেমে মোটর সোল্ডারিং এবং সেন্সর মাউন্টিং সম্পন্ন করা।
* [ ] **Wiring Check:** শর্ট সার্কিট টেস্ট (Multimeter continuity test) করা।
* [ ] **PX4 Flashing:** Pixhawk-এ PX4 v1.14+ ফ্ল্যাশ করা।
* [ ] **Calibration:** Accel, Gyro, Compass, Radio এবং ESC ক্যালিব্রেট করা।
* [ ] **Manual Flight:** Stabilize মোডে ম্যানুয়াল উড্ডয়ন এবং ভারসাম্য পরীক্ষা করা।
* [ ] **Companion Link:** Jetson এবং Pixhawk-এর মাঝে ROS 2/Micro-XRCE কমুনিকেশন তৈরি করা।
* [ ] **Auto Flight:** `takeoff_and_hover.py` দিয়ে সফলভাবে ২ মিটার স্বায়ত্তশাসিত টেক-অফ ও ল্যান্ডিং ভ্যালিডেট করা।

```
