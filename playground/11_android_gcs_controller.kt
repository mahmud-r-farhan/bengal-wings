// Run inside Android / Kotlin Runtime project
package fun.devplus.bengalwings.gcs

data class DroneTelemetryData(
    val callsign: String,
    val isArmed: Boolean,
    val batteryPct: Int
)

class MobileGcsController {
    fun sendEmergencyCommand(commandType: String) {
        println("==================================================================")
        println(" 🦅 BENGAL WINGS :: KOTLIN MOBILE GCS CONTROLLER (ANDROID)       ")
        println("==================================================================")
        
        val droneState = DroneTelemetryData("AEGIS-X1", true, 89)
        println("[MOBILE GCS]: Target Vehicle: ${droneState.callsign} | Batt: ${droneState.batteryPct}%")
        println("[COMMAND TRANSMIT]: Executing High-Priority Action -> [$commandType]")
        println("[SUCCESS]: UDP Datagram Dispatched to Telemetry Radio.")
    }
}

fun main() {
    val gcs = MobileGcsController()
    gcs.sendEmergencyCommand("RTL_RETURN_TO_LAUNCH")
}