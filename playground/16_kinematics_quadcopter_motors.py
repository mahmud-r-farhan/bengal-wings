# Run with: python3 16_kinematics_quadcopter_motors.py

def calculate_quad_motor_speeds(throttle, roll, pitch, yaw):
    """
    Standard Quad-X Kinematics Mixer Matrix:
    M1 (Front-Right CCW) = Throttle - Roll + Pitch + Yaw
    M2 (Rear-Right  CW ) = Throttle - Roll - Pitch - Yaw
    M3 (Rear-Left   CCW) = Throttle + Roll - Pitch + Yaw
    M4 (Front-Left  CW ) = Throttle + Roll + Pitch - Yaw
    """
    m1 = throttle - roll + pitch + yaw
    m2 = throttle - roll - pitch - yaw
    m3 = throttle + roll - pitch + yaw
    m4 = throttle + roll + pitch - yaw

    # Constrain within valid PWM Motor range (1000us to 2000us)
    motors = [m1, m2, m3, m4]
    constrained_motors = [max(1000, min(2000, int(m))) for m in motors]
    return constrained_motors

def run_kinematics_test():
    print("==================================================================")
    print(" 🦅 BENGAL WINGS :: QUAD-ROTOR KINEMATICS & MOTOR PWM MIXER       ")
    print("==================================================================")

    # Input Commands (Throttle, Roll, Pitch, Yaw)
    test_inputs = [
        {"name": "Hover", "throttle": 1500, "roll": 0, "pitch": 0, "yaw": 0},
        {"name": "Roll Right", "throttle": 1600, "roll": 100, "pitch": 0, "yaw": 0},
        {"name": "Pitch Forward", "throttle": 1600, "roll": 0, "pitch": 150, "yaw": 0},
    ]

    for test in test_inputs:
        m = calculate_quad_motor_speeds(test["throttle"], test["roll"], test["pitch"], test["yaw"])
        print(f"Command [{test['name']:<13}] -> M1(FR): {m[0]}us | M2(RR): {m[1]}us | M3(RL): {m[2]}us | M4(FL): {m[3]}us")

if __name__ == '__main__':
    run_kinematics_test()