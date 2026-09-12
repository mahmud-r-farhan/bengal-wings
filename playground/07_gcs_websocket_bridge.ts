// Run with: npx ts-node 07_gcs_websocket_bridge.ts
interface DroneTelemetry {
    droneId: string;
    altitude: number;
    status: 'ARMED' | 'DISARMED' | 'OFFBOARD';
    batteryVoltage: number;
}

class TelemetryBroadcaster {
    private droneId: string;

    constructor(id: string) {
        this.droneId = id;
    }

    public startBroadcast(): void {
        console.log(`==================================================================`);
        console.log(` 🦅 BENGAL WINGS :: TYPESCRIPT GCS WEBSOCKET BROADCASTER          `);
        console.log(`==================================================================`);
        console.log(`[WS BUS]: Listening on ws://127.0.0.1:8080/telemetry...`);

        let count = 0;
        const interval = setInterval(() => {
            count++;
            const data: DroneTelemetry = {
                droneId: this.droneId,
                altitude: Number((Math.random() * 25 + 2).toFixed(2)),
                status: 'OFFBOARD',
                batteryVoltage: Number((24.5 - count * 0.1).toFixed(2))
            };

            console.log(`[WS EMIT]: ${JSON.stringify(data)}`);

            if (count >= 5) {
                clearInterval(interval);
                console.log(`[WS BUS]: Telemetry Session Closed.`);
            }
        }, 400);
    }
}

const broadcaster = new TelemetryBroadcaster("AEGIS-WING-01");
broadcaster.startBroadcast();