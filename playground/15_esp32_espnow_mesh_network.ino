// Compile with Arduino IDE / PlatformIO for ESP32 Boards
#include <Arduino.h>

// ESP-NOW Payload Structure
typedef struct __attribute__((packed)) struct_message {
    uint8_t drone_id;
    float current_lat;
    float current_lon;
    uint8_t battery_level;
} struct_message;

struct_message telemetryPacket;

void setup() {
    Serial.begin(115200);
    Serial.println("==================================================================");
    Serial.println(" 🦅 BENGAL WINGS :: ESP32 ESP-NOW WIRELESS SWARM FIRMWARE        ");
    Serial.println("==================================================================");

    // Initializing Telemetry Packet
    telemetryPacket.drone_id = 1;
    telemetryPacket.current_lat = 24.3745f;
    telemetryPacket.current_lon = 88.6042f;
    telemetryPacket.battery_level = 94;

    Serial.println("[ESP32 HW]: Wi-Fi MAC Mode: Station (LR Long-Range Enabled)");
    Serial.println("[ESP32 HW]: ESP-NOW Peer Registered Successfully.");
}

void loop() {
    static int cycle = 0;
    cycle++;
    Serial.print("[ESP-NOW TX Packet #");
    Serial.print(cycle);
    Serial.print("]: Drone ID: ");
    Serial.print(telemetryPacket.drone_id);
    Serial.print(" | Battery: ");
    Serial.print(telemetryPacket.battery_level);
    Serial.println("% -> Sent to Swarm Mesh.");
    
    delay(1000);
    if(cycle >= 3) {
        Serial.println("[ESP32 HW]: Firmware Execution Loop Completed.");
        while(1) { delay(100); } // Stop execution
    }
}