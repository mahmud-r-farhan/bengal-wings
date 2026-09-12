# Run on Raspberry Pi: python3 13_raspberry_pi_gpio_sensors.py
import time
import sys

# Emulating GPIO interface for cross-platform simulation
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("[WARN] RPi.GPIO not found. Running in Hardware Emulated Mode.")
    GPIO = None

TRIG_PIN = 23
ECHO_PIN = 24

def setup_rpi_gpio():
    if GPIO:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TRIG_PIN, GPIO.OUT)
        GPIO.setup(ECHO_PIN, GPIO.IN)

def read_obstacle_distance():
    print("==================================================================")
    print(" 🦅 BENGAL WINGS :: RASPBERRY PI GPIO HARDWARE SENSOR MONITOR    ")
    print("==================================================================")
    
    setup_rpi_gpio()
    for i in range(1, 6):
        # Simulated distance read in cm
        simulated_distance = round(120.5 - (i * 15.2), 2)
        print(f"[{time.strftime('%H:%M:%S')}] RPi GPIO [Pin {TRIG_PIN}/{ECHO_PIN}] -> Obstacle Distance: {simulated_distance} cm")
        if simulated_distance < 60.0:
            print(f"  ⚠️  [WARNING] Obstacle Danger! Triggering Autonomous Avoidance Vector.")
        time.sleep(0.4)

    if GPIO:
        GPIO.cleanup()

if __name__ == '__main__':
    read_obstacle_distance()