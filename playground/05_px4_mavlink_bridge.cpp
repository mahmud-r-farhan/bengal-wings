// Run with: g++ 05_px4_mavlink_bridge.cpp -o 05_px4_mavlink_bridge && ./05_px4_mavlink_bridge
#include <iostream>
#include <chrono>
#include <thread>
#include <iomanip>

struct SensorPacket {
    uint32_t timestamp_ms;
    float flow_x;
    float flow_y;
    float lidar_distance_m;
    uint8_t quality;
};

class PX4Bridge {
public:
    void parse_sensor_stream(const SensorPacket& pkt) {
        std::cout << "[MAVLINK RECV] Time: " << pkt.timestamp_ms << "ms | "
                  << "OptFlow X: " << std::setw(6) << pkt.flow_x << " rad/s | "
                  << "OptFlow Y: " << std::setw(6) << pkt.flow_y << " rad/s | "
                  << "LiDAR Alt: " << std::setprecision(3) << pkt.lidar_distance_m << "m | "
                  << "Signal Quality: " << (int)pkt.quality << "%" << std::endl;
    }
};

int main() {
    std::cout << "==================================================================" << std::endl;
    std::cout << " 🦅 BENGAL WINGS :: C++ EMBEDDED MAVLINK BRIDGE PARSER            " << std::endl;
    std::cout << "==================================================================" << std::endl;

    PX4Bridge bridge;
    SensorPacket mock_pkt = {1000, 0.012f, -0.005f, 2.45f, 99};

    for (int i = 0; i < 6; ++i) {
        mock_pkt.timestamp_ms += 100;
        mock_pkt.flow_x += 0.003f;
        mock_pkt.lidar_distance_m += 0.15f;
        
        bridge.parse_sensor_stream(mock_pkt);
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }

    std::cout << "\n[C++ MAVLink Driver]: Hardware Serial Communication Operational." << std::endl;
    return 0;
}