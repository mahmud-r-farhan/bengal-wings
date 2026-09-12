// Run with: rustc 01_flight_telemetry_sim.rs && ./01_flight_telemetry_sim
use std::thread;
use std::time::Duration;

struct DroneState {
    altitude_m: f32,
    velocity_ms: f32,
    battery_pct: u8,
    mode: String,
    pos_x: f32,
    pos_y: f32,
}

fn main() {
    println!("\x1B[2J\x1B[1;1H"); // Clear Terminal Screen
    println!("==================================================================");
    println!(" 🦅 BENGAL WINGS :: RUST CORE FLIGHT TELEMETRY SIMULATOR v1.0 ");
    println!("==================================================================");

    let mut state = DroneState {
        altitude_m: 0.0,
        velocity_ms: 0.0,
        battery_pct: 100,
        mode: String::from("TAKEOFF_INIT"),
        pos_x: 0.0,
        pos_y: 0.0,
    };

    let waypoints: [(f32, f32); 4] = [(12.5, 8.4), (25.0, 19.2), (30.1, 45.8), (0.0, 0.0)];

    for (step, target) in waypoints.iter().enumerate() {
        state.mode = format!("NAVIGATING_WAYPOINT_{}", step + 1);
        
        for _ in 0..5 {
            thread::sleep(Duration::from_millis(400));
            
            // Simulating Physics Dynamics
            if state.altitude_m < 15.0 {
                state.altitude_m += 1.5;
            }
            state.velocity_ms = 4.2 + (step as f32 * 0.5);
            state.pos_x += (target.0 - state.pos_x) * 0.25;
            state.pos_y += (target.1 - state.pos_y) * 0.25;
            state.battery_pct -= 1;

            print!("\x1B[5;1H"); // Move cursor to top
            println!("[MODE]: \x1B[32m{}\x1B[0m                        ", state.mode);
            println!("[ALTITUDE]: {:.2} meters", state.altitude_m);
            println!("[VELOCITY]: {:.2} m/s", state.velocity_ms);
            println!("[LALS COORDS]: X: {:.3}m | Y: {:.3}m | Z: {:.2}m", state.pos_x, state.pos_y, state.altitude_m);
            println!("[BATTERY LEVEL]: \x1B[33m{}%\x1B[0m", state.battery_pct);
            println!("------------------------------------------------------------------");
            println!("Status: [FCU: OK] [Optical Flow: ACTIVE] [SLAM: LOCK] [LALS: SYNC]");
        }
    }

    println!("\n\x1B[32m[SUCCESS]: Waypoint Mission Completed. Hovering at Base Base.\x1B[0m");
}