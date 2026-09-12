
# Edge Artificial Intelligence & Target Detection Pipeline

## 1. Computer Vision Architecture (YOLOv10 + TensorRT)

সার্ভারের সহায়তা ছাড়া ড্রোনের ভেতরেই উচ্চগতিতে প্রসেসিং নিশ্চিত করার জন্য **YOLOv10 (Nano/Small)** মডেলটি **NVIDIA TensorRT Engine**-এ কনভার্ট করে রান করা হয়।

### Model Performance Metrics Target

-   **Target Inference Speed:** >= 35 Frames Per Second (FPS).
    
-   **Target Precision (mAP@0.5):** >= 88.5%.
    
-   **Precision Format:** FP16 (Half Precision) / INT8 Quantized.
    

## 2. Threat Classes & Dataset Customization

মডেলটিকে নির্দিষ্ট কিছু ক্লাসের ওপর কাস্টম ফাইন-টিউনিং করা হয়েছে:

YAML

```
names:
  0: Armed Infantry
  1: Unarmed Human
  2: Military Tank / Armored Vehicle
  3: Civilian Vehicle
  4: Hostile UAV / Drone
  5: Concealed Weapon / Weapon Cache

```

## 3. Pixel Coordinate to Real-World Coordinate Mapping

ক্যামেরায় কোনো শত্রু যানবাহন বা বস্তু ধরা পড়লে তার পিক্সেল ভ্যালুকে বাস্তব মানচিত্রের কোঅর্ডিনেটে রূপান্তর করার পদ্ধতি:

$$\begin{bmatrix} X_{world} \\ Y_{world} \\ Z_{world} \end{bmatrix} = R_{drone} \times \left( Z_{depth} \cdot K^{-1} \begin{bmatrix} u_{pixel} \\ v_{pixel} \\ 1 \end{bmatrix} \right) + T_{drone}$$

কোথায়:

-   $K$ = Camera Intrinsic Matrix (ফোকাল লেন্থ ও অপটিক্যাল সেন্টার)।
    
-   $Z_{depth}$ = ডিপথ ক্যামেরা বা পয়েন্ট ক্লাউড থেকে প্রাপ্ত অবজেক্টের দূরত্ব।
    
-   $R_{drone}, T_{drone}$ = SLAM ও LALS থেকে প্রাপ্ত ড্রোনের নিজস্ব ঘূর্ণন (Rotation) এবং অবস্থান (Translation) ভেক্টর।
    

## 4. Threat Decision Matrix & Autonomous Action

```
                              [ YOLO Target Detection ]
                                          │
                                          ▼
                             Is Confidence Score > 75%?
                                   │            │
                         YES ──────┘            └────── NO ──► Ignore / Continue Scan
                          │
                          ▼
                 Check Target Classification
                          │
     ┌────────────────────┼────────────────────┐
     ▼                    ▼                    ▼
[ Armed Infantry ]   [ Hostile Drone ]   [ Armored Vehicle ]
     │                    │                    │
     ▼                    ▼                    ▼
Priority: HIGH       Priority: CRITICAL   Priority: HIGH
Action: Lock Track   Action: Alert Anti-  Action: Mark Map &
& Send Coordinate    Drone Jammer System  Notify Base Command
```