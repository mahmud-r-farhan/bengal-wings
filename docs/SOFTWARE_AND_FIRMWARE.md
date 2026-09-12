
# Software Stack, Firmware Architecture & Navigation Engine

## 1. Flight Controller Firmware Configuration (PX4 Autopilot)

আমরা **PX4 Autopilot (v1.14+)** ব্যবহার করছি কারণ এর আর্কিটেকচার অত্যন্ত সুরক্ষিত এবং মডিউলার।

-   **Estimator Engine:** EKF2 (Extended Kalman Filter 2).
    
-   **GPS-Disabled Parameters:**
    
    -   `EKF2_GPS_CTRL = 0` (GPS ইনপুট সম্পূর্ণ নিষ্ক্রিয় করা থাকবে)।
        
    -   `EKF2_EV_CTRL = 15` (External Vision Position, Yaw, Height ডেটা সক্রিয় করা থাকবে)।
        
    -   `EKF2_HGT_MODE = 2` (Primary Height Reference হিসেবে Rangefinder/LiDAR নির্দেশিত থাকবে)।
        

## 2. ROS 2 (Humble / Jazzy) Middleware Architecture

Jetson Orin Nano-তে চলমান সমস্ত সাব-সিস্টেম **ROS 2**-এর নোড হিসেবে কাজ করবে।

```
                                  ROS 2 NODE ARCHITECTURE

  ┌─────────────────────────┐
  │ RealSense Stereo Node   ├───────► /camera/image_raw ─────┐
  └─────────────────────────┘                                │
                                                             ▼
  ┌─────────────────────────┐                     ┌────────────────────┐
  │ LALS UWB Positioning    ├───────► /lals/pose ├►│ Pose Fusion Node   ├─► /mavros/vision_pose/pose
  └─────────────────────────┘                     └────────────────────┘            │
                                                             ┌──────────────────────┘
  ┌─────────────────────────┐                                ▼
  │ Optical Flow & LiDAR    ├───────► /sensor/range ──► [ MAVROS Bridge ]
  └─────────────────────────┘                                │
                                                             ▼ (Serial MAVLink @ 921600 Baud)
                                                    [ PX4 Autopilot FCU ]

```

## 3. Visual SLAM & Path Planning Pipeline

জিপিএস ছাড়া নিজের পজিশন বের করার জন্য **ORB-SLAM3** ব্যবহার করা হচ্ছে।

### Core Algorithm Workflow:

1.  **Feature Extraction:** ক্যামেরা ফিড থেকে প্রতি ফ্রেমে ২০০-৫০০টি জ্যামিতিক পয়েন্ট (Corners, Edges) সনাক্ত করা হয়।
    
2.  **Triangulation:** ক্রমাগত ফ্রেম পরিবর্তনের ওপর ভিত্তি করে আশপাশের ৩ডি এনভায়রনমেন্ট তৈরি হয়।
    
3.  **Loop Closure Detection:** পূর্বে অতিক্রম করা কোনো জায়গা ড্রোন আবার দেখতে পেলে তার সঞ্চিত এরর কারেক্ট করে পজিশনিং ড্রিপ্ট শূন্যের কোঠায় নামিয়ে আনে।
    

## 4. Ground Control Station (GCS) Software

-   **Framework:** Flutter Desktop Engine / Web-based Dashboard.
    
-   **Communication Protocol:** MAVLink over UDP/TCP socket with 256-bit AES encryption.
    
-   **Features:**
    
    -   রিয়েল-টাইম AI ডিটেকশন বক্স উইথ টার্গেট পজিশন কোঅর্ডিনেট।
        
    -   ৩ডি স্লেম ম্যাপ ভিজ্যুয়ালাইজেশন।
        
    -   অটোনোমাস ওয়েপয়েন্ট মিশন কম্যান্ড।