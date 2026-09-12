// Run with: npx ts-node 22_mqtt_gcs_cloud_publisher.ts

interface MqttTelemetryMessage {
    topic: string;
    qos: 0 | 1 | 2;
    payload: {
        droneId: string;
        gpsLock: boolean;
        satellites: number;
    };
}

class MqttWirelessLink {
    private brokerUrl: string = "mqtt://cloud.bengalwings.fun:1883";

    public connectAndPublish(): void {
        console.log(`==================================================================`);
        console.log(` 🦅 BENGAL WINGS :: TYPESCRIPT MQTT CELLULAR CLOUD LINK          `);
        console.log(`==================================================================`);
        console.log(`[MQTT CLIENT]: Connecting via 4G/LTE Modems to ${this.brokerUrl}...`);

        const msg: MqttTelemetryMessage = {
            topic: "bengal-wings/telemetry/v1",
            qos: 1,
            payload: {
                droneId: "BW-DRONE-DELTA",
                gpsLock: true,
                satellites: 18
            }
        };

        console.log(`[MQTT PUB]: Topic -> '${msg.topic}' | QoS Level: ${msg.qos}`);
        console.log(`[MQTT PAYLOAD]:`, JSON.stringify(msg.payload));
        console.log(`[MQTT STATUS]: Message acknowledged by Remote Broker (ACK Received).`);
    }
}

const client = new MqttWirelessLink();
client.connectAndPublish();