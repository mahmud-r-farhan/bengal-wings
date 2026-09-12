# 🚁 Phase 01 Starter Plan: AI Reconnaissance & Autonomous Mapping Setup

> **Project Goal:** Build an autonomous GPS-denied reconnaissance & 3D mapping drone powered by Edge AI.  
> **Target Phase:** Phase 01 — Baseline Hardware Integration, Firmware Setup, Simulation & Edge AI Pipeline.  
> **Status:** Execution Ready  

---

## 📑 Executive Summary

এই ডকুমেন্টে একটি AI-চালিত স্বায়ত্তশাসিত সার্ভেইল্যান্স ও ম্যাপিং ড্রোন শূন্য থেকে বানিয়ে ড্রোনে ইমপ্লিমেন্ট করার ধাপে ধাপে নির্দেশিকা দেওয়া হয়েছে। Phase 01-এর প্রধান লক্ষ্য হলো ড্রোন ফ্রেম অ্যাসেম্বলি, ফ্লাইট কন্ট্রোলার কনফিগারেশন, ROS 2 চালিত পজিশনিং ফিল্টার এবং NVIDIA Jetson-এ এজ-এআই (Edge AI) সিস্টেম ইমপ্লিমেন্ট করা।

---

## 🏗️ Phase 01 Roadmap & Architecture


```

┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PHASE 01 IMPLEMENTATION                                │
├───────────────────────────────┬───────────────────────────────┬────────────────────────┤
│     STEP 1: HARDWARE SETUP    │     STEP 2: FIRMWARE & ROS2   │   STEP 3: EDGE AI PIPELINE│
│  - Carbon Frame Assembly      │  - PX4 Autopilot Setup        │  - TensorRT Engine     │
│  - ESC & Brushless Motors     │  - Micro-XRCE-DDS Agent       │  - Real-Time Camera    │
│  - Pixhawk FC + Jetson Orin   │  - Optical Flow & LiDAR EKF   │  - Target Detection    │
└───────────────────────────────┴───────────────────────────────┴────────────────────────┘

```

---

## 🧰 Step 1: Hardware Assembly & Electrical Setup

### 1.1 Physical Component Assembly
1. **Airframe Build:** 7-ইঞ্চি কার্বন ফাইবার ফ্রেমে মোটরগুলা (2806.5 1300KV) মাউন্ট করুন এবং ভাইব্রেশন কমানোর জন্য এন্টি-ভাইব্রেশন ড্যাম্পেনার ব্যবহার করুন।
2. **Flight Controller (Pixhawk 6C):** ড্রোনের সেন্টার অফ গ্র্যাভিটিতে (Center of Gravity - CG) Pixhawk সেট করুন।
3. **Companion Computer (NVIDIA Jetson Orin Nano):** ড্রোনের ওপরের প্লেটে একটি কুলিং ফ্যান সহ মাউন্ট করুন।
4. **Sensors:**
   - **Downward Sensors:** Optical Flow Sensor (PMW3901) এবং LiDAR (Benewake TFmini) ড্রোনের নিচের দিকে সমান্তরালভাবে মাউন্ট করুন।
   - **Front Sensor:** Stereo Camera (Intel RealSense D435i / ZED Mini) ড্রোনের সামনের দিকে মাউন্ট করুন।

### 1.2 Power Distribution
- ব্যাটারির direct 6S (22.2V - 25.2V) পাওয়ার যাবে 4-in-1 ESC-তে।
- Step-down Buck Converter (12V 5A) ব্যবহার করে Jetson Orin Nano-তে পাওয়ার দিন।
- Pixhawk FC-তে Power Module থেকে ৫.২V কানেকশন নিশ্চিত করুন।

---

## 🕹️ Step 2: Firmware & Software Navigation Architecture

### 2.1 Flight Controller Setup (PX4 Autopilot)
1. **QGroundControl (QGC)** ওপেন করে Pixhawk-এ PX4 Autopilot (v1.14+) বার্ন করুন।
2. **GPS-Denied EKF2 Config:** জিপিএস ছাড়া ইনডোর বা জ্যামিং পরিবেশে চলার জন্য QGC থেকে নিচের পরামিতিগুলো সেট করুন:
   - `EKF2_GPS_CTRL = 0` (GPS বন্ধ রাখা)
   - `EKF2_EV_CTRL = 15` (External Vision/Optical Flow পজিশনিং চালু করা)
   - `EKF2_HGT_MODE = 2` (Rangefinder/LiDAR অনুযায়ী উচ্চতা নির্ধারণ)

### 2.2 Companion Computer & ROS 2 Environment Setup
1. Jetson Orin Nano-তে **Ubuntu 22.04 LTS (JetPack 6.x)** ইনস্টল করুন।
2. **ROS 2 Humble / Jazzy** এবং Micro-XRCE-DDS এজেন্ট সেটআপ করুন:
   ```bash
   sudo apt update && sudo apt install ros-humble-desktop git python3-pip -y
   git clone [https://github.com/eProsima/Micro-XRCE-DDS-Agent.git](https://github.com/eProsima/Micro-XRCE-DDS-Agent.git)
   cd Micro-XRCE-DDS-Agent && mkdir build && cd build
   cmake .. && make && sudo make install && sudo ldconfig

```

3. **Pixhawk to Jetson Serial Communication Start:**
```bash
MicroXRCEAgent serial --dev /dev/ttyTHS1 -b 921600

```



---

## 🧠 Step 3: Edge AI Threat Detection Implementation

### 3.1 YOLOv10 to TensorRT Compilation

Jetson-এ কম ল্যাটেন্সি এবং ৩০+ FPS ডিটেকশন পাওয়ার জন্য YOLOv10 মডেলকে TensorRT FP16 ইঞ্জিনে কনভার্ট করুন:

```bash
# Export PyTorch Model to TensorRT Engine
pip install ultralytics
yolo export model=yolov10n.pt format=engine half=True device=0

```

### 3.2 Real-Time Detection Inference Node (`ai_recon_node.py`)

ড্রোনের ক্যামেরা থেকে ফ্রেম নিয়ে অবজেক্ট ডিটেক্ট করার জন্য ROS 2 Python নোড লিখুন:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class ReconAINode(Node):
    def __init__(self):
        super().__init__('ai_recon_node')
        self.subscription = self.create_subscription(Image, '/camera/color/image_raw', self.image_callback, 10)
        self.bridge = CvBridge()
        self.model = YOLO('yolov10n.engine') # Loaded TensorRT Engine

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(frame, stream=True)
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > 0.5:
                    self.get_logger().info(f"Target Detected: Class {cls_id} with {conf:.2f} Confidence")

def main(args=None):
    rclpy.init(args=args)
    node = ReconAINode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

```

---

## 🗺️ Step 4: 3D Mapping & Autonomous Navigation Pipeline

1. **Depth Camera Integration:** Intel RealSense D435i ROS 2 ড্রাইভার ইনস্টল করুন।
2. **RTAB-Map (Real-Time Appearance-Based Mapping):** GPS ছাড়া পয়েন্ট ক্লাউড (Point Cloud) 3D ম্যাপ জেনারেট করার জন্য RTAB-Map ইনস্টল করুন:
```bash
sudo apt install ros-humble-rtabmap-ros

```


3. **Map Generation Command:**
```bash
ros2 launch rtabmap_cli rtabmap.launch.py \
    rtabmap_args:="--delete_db_on_start" \
    depth_topic:=/camera/depth/image_rect_raw \
    rgb_topic:=/camera/color/image_raw \
    camera_info_topic:=/camera/color/camera_info

```



---

## 📋 Phase 01 Task Breakdown & Checklist

* [ ] **Hardware Build:** কার্বন ফাইবার ফ্রেম, প্রোপালশন, পিক্সহক এবং জেটসন ওরিণ মাউন্ট সম্পূর্ণ করা।
* [ ] **Power Check:** Multimeter দিয়ে 12V Buck Converter এবং 5V Pixhawk পাওয়ার ভোল্টেজ ঠিক আছে কিনা চেক করা।
* [ ] **Firmware Calibration:** QGroundControl দিয়ে IMU, Compass, ESC Calibration সম্পন্ন করা।
* [ ] **Serial Bridge:** Pixhawk $\leftrightarrow$ Jetson Telemetry (Micro-XRCE-DDS) যোগাযোগ নিশ্চিত করা।
* [ ] **Sensors Integration:** Optical Flow এবং Rangefinder কাজ করছে কিনা টেস্ট করা (`listener sensor_combined` কমান্ড দিয়ে)।
* [ ] **AI Model Test:** Jetson-এ কাস্টম YOLOv10 FP16 Engine রিয়েল-টাইমে ৩০ FPS প্রসেস করছে কিনা ভ্যালিডেট করা।
* [ ] **3D Mapping:** RTAB-Map ব্যবহার করে ইনডোর বা বাউন্ডারি এলাকার 3D Point Cloud ম্যাপ তৈরি করা।
* [ ] **Flight Test:** GPS-Denied স্বায়ত্তশাসিত টেক-অফ, পজিশন হোল্ড (Hovering) এবং ল্যান্ডিং ফিল্ড টেস্ট করা।

```

---