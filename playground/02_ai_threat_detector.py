# Run with: python3 02_ai_threat_detector.py
import time
import random

THREAT_CLASSES = ["Armed Infantry", "Armored Vehicle", "Hostile UAV", "Unattended Object"]

def render_threat_feed():
    print("\033[H\033[J", end="") # Clear Terminal
    print("==================================================================")
    print(" 🦅 BENGAL WINGS :: EDGE AI THREAT DETECTION MONITOR (YOLOv10) ")
    print("==================================================================")
    print("Processing Pipeline: Video Stream 1080p @ 30fps -> TensorRT FP16 Engine\n")

    for i in range(1, 15):
        time.sleep(0.5)
        threat = random.choice(THREAT_CLASSES)
        confidence = round(random.uniform(78.5, 98.9), 2)
        pixel_x = random.randint(100, 1920)
        pixel_y = random.randint(100, 1080)
        
        # Real-World Map Coordinates via Geometry Mapping
        map_x = round(random.uniform(5.0, 120.0), 2)
        map_y = round(random.uniform(10.0, 150.0), 2)

        color_code = "\033[91m" if threat in ["Armed Infantry", "Hostile UAV"] else "\033[93m"
        
        print(f"[{time.strftime('%H:%M:%S')}] Frame #{i*30:04d} -> "
              f"Detected: {color_code}{threat:<18}\033[0m | "
              f"Conf: {confidence}% | "
              f"Bounding Box: [{pixel_x}, {pixel_y}] | "
              f"World Pos: ({map_x}m, {map_y}m)")
        
        if threat == "Hostile UAV":
            print("\033[91m [ALERT]: Hostile UAV Tracked! Initiating Counter-Jammer Protocol...\033[0m")

if __name__ == "__main__":
    try:
        render_threat_feed()
    except KeyboardInterrupt:
        print("\n[AI Inference Stream Stopped]")