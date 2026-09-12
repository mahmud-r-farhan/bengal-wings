
# Local Area Positioning System (LALS) — Engineering, Hardware & Test Suite

## 1. Principle of Operation & Trilateration Math

**LALS (Local Area Positioning System)** হলো জিপিএস-বিহীন স্থানে সুনির্দিষ্ট পজিশন পাওয়ার জন্য একটি লোকাল রেডিও সিস্টেম। এটি **Decawave UWB (Ultra-Wideband)** টেকনোলজি ব্যবহার করে টু-ওয়ে রেঞ্জিং (TWR) চালনা করে।

```
                                  Anchor 2 (0, Y_max, Z2)
                                       ▲
                                      / \
                                     /   \
                                    /     \
                                   /  d2   \
                                  /         \
  Anchor 1 (0, 0, Z1) ───────────/─── d1 ─── \─────────── Anchor 3 (X_max, 0, Z3)
                                 \          /
                                  \   d3   /
                                   \      /
                                    \    /
                                     \  /
                                      ▼
                           AEGIS-X Drone (x, y, z)

```

তিনটি নির্দিষ্ট স্থানের অ্যাঙ্কর থেকে ড্রোনের রেডিও তরঙ্গের যাতায়াতের সময় (Time-of-Flight) মেপে দূরত্ব $d_1, d_2, d_3$ বের করা হয়:

$$d_i = c \times \Delta t_i$$

এরপর ট্রাইলেটারেশন (Trilateration) সমীকরণের সাহায্যে ড্রোনের অবস্থান $(x,y,z)$ হিসাব করা হয়:

$$(x - x_i)^2 + (y - y_i)^2 + (z - z_i)^2 = d_i^2$$

## 2. Hardware PCB Schematic & Component List

LALS সিস্টেমে দুটি ভিন্ন ডিভাইস থাকে:

1.  **LALS Anchor** (স্থায়ী রেডিও টাওয়ার বা ট্রাইপড)।
    
2.  **LALS Tag / Rover** (ড্রোনে সংযুক্ত পিসিবি)।
    

### LALS Board BOM (Bill of Materials)

-   **UWB Chipset:** Decawave / Qorvo **DWM3000 Module** (Supports IEEE 802.15.4z UWB standard).
    
-   **Main Microcontroller:** STM32F401RET6 (ARM Cortex-M4 @ 84MHz) / ESP32-S3 (for debug).
    
-   **Antenna:** Custom Omnidirectional UWB PCB Trace Antenna (Channel 5: 6.5 GHz & Channel 9: 8 GHz).
    
-   **Power Management:** High Efficiency Buck-Boost Regulator (TPS63020) for stable 3.3V supply.
    
-   **Interface:** SPI for DWM3000 to MCU communication; UART for MCU to Jetson communication.
    

## 3. Firmware Source Code Prototype for LALS Rover (`lals_rover.cpp`)

C++

```
#include <Arduino.h>
#include <SPI.h>
#include "DW1000.h"

// Hardware Pin Definitions
#define PIN_RST 9
#define PIN_IRQ 2
#define PIN_SS 10

typedef struct {
  float x;
  float y;
  float z;
} Position;

Position currentPose = {0.0f, 0.0f, 0.0f};

void setup() {
  Serial.begin(115200);
  DW1000.begin(PIN_IRQ, PIN_RST);
  DW1000.select(PIN_SS);
  DW1000.newConfiguration();
  DW1000.setDefaults();
  DW1000.setDeviceAddress(5); // Tag ID
  DW1000.setNetworkId(10);
  DW1000.commitConfiguration();
  Serial.println(F("LALS Rover Module Initialized."));
}

void computeTrilateration(float d1, float d2, float d3) {
  // Simplified 2D Trilateration for fast edge execution
  // Anchor 1 at (0,0), Anchor 2 at (d_a12, 0), Anchor 3 at (i, j)
  float x = (pow(d1, 2) - pow(d2, 2) + pow(5.0, 2)) / (2 * 5.0);
  float y = ((pow(d1, 2) - pow(d3, 2) + pow(5.0, 2) + pow(5.0, 2)) / (2 * 5.0)) - (5.0 / 5.0) * x;
  
  currentPose.x = x;
  currentPose.y = y;
  currentPose.z = 1.5; // Altitude backed by LiDAR

  // Output MAVLink-compatible JSON stream over UART to ROS 2
  Serial.print("{\"x\":"); Serial.print(currentPose.x);
  Serial.print(",\"y\":"); Serial.print(currentPose.y);
  Serial.print(",\"z\":"); Serial.print(currentPose.z);
  Serial.println("}");
}

void loop() {
  // Read distance metrics from Anchor 1, 2, 3
  float d1 = DW1000.getDistance(1);
  float d2 = DW1000.getDistance(2);
  float d3 = DW1000.getDistance(3);
  
  computeTrilateration(d1, d2, d3);
  delay(20); // 50 Hz Update Rate
}

```

## 4. Real-World Manufacturing & Fabrication Process

### Step 1: PCB Design & Layer Stack-Up

-   **4-Layer Printed Circuit Board:**
    
    -   Layer 1 (Top): High-Speed UWB RF Signals & Component Placement.
        
    -   Layer 2 (Ground): Continuous Solid Ground Plane for RF Shielding.
        
    -   Layer 3 (Power): Power Traces (3.3V & 5V).
        
    -   Layer 4 (Bottom): Digital Logic & Interface Traces.
        

### Step 2: Enclosure Fabrication

-   Anchor & Rover এনক্লেজারগুলো **PETG / Carbon-Fiber Reinforced Polycarbonate** উপাদানে ৩ডি প্রিন্ট করা হবে যা ওয়াটারপ্রুফ (IP65 standard compliant)।
    

## 5. Industrial Real-World Test Cases & Protocol

### Test Case LALS-01: Line-of-Sight (LOS) Precision Test

-   **Objective:** ড্রোনের পজিশনিং নির্ভুলতা সেন্টিমিটার লেভেলে পরীক্ষা করা।
    
-   **Setup:** একটি ২০m x ২০m খোলা মাঠে ৩টি LALS Anchor ত্রিপদে মাউন্ট করা হবে।
    
-   **Acceptance Criteria:** ড্রোনের পজিশনে ±৫ সেন্টিমিটারের বেশি বিচ্যুতি (Error Deviation) থাকা চলবে না।
    

### Test Case LALS-02: RF Jamming Resiliency Test

-   **Objective:** জিপিএস জ্যামার সক্রিয় অবস্থায় LALS নেভিগেশনের কার্যকারিতা নিশ্চিত করা।
    
-   **Setup:** টেস্ট এলাকায় একটি জিপিএস জ্যামার চালু করা হবে যাতে জিপিএস সিগন্যাল সম্পূর্ণ লস্ট হয়ে যায়।
    
-   **Acceptance Criteria:** ড্রোন যেন জিপিএস বিচ্ছিন্নতা টের পাওয়ার সাথে সাথে শূন্য ড্রিপ্ট ছাড়া স্বয়ংক্রিয়ভাবে LALS পজিশনিং স্কিমে সুইচেস করে স্থির হয়ে উড়তে পারে (Position Hold)।


> by Mahmud Rahman