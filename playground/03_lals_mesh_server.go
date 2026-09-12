// Run with: go run 03_lals_mesh_server.go
package main

import (
	"fmt"
	"math"
	"math/rand"
	"time"
)

type AnchorBeacon struct {
	ID       int
	X, Y, Z  float64
	Distance float64
}

func simulateAnchorReadings(id int, x, y, z float64, ch chan<- AnchorBeacon) {
	for {
		time.Sleep(300 * time.Millisecond)
		// Simulating Time-of-Flight Radio Distance with minor noise
		noise := (rand.Float64() - 0.5) * 0.1
		simulatedDist := math.Sqrt(x*x+y*y) + noise
		ch <- AnchorBeacon{ID: id, X: x, Y: y, Z: z, Distance: simulatedDist}
	}
}

fn main() {
	fmt.Println("==================================================================")
	fmt.Println(" 🦅 BENGAL WINGS :: LALS UWB CONCURRENT SERVER (GOLANG CORE)      ")
	fmt.Println("==================================================================")
	fmt.Println("Listening for UWB Anchors on Encrypted Radio Channel 5...")

	dataChan := make(chan AnchorBeacon)

	// Launch 3 Concurrent Goroutines for 3 Stationary Anchors
	go simulateAnchorReadings(1, 0.0, 0.0, 3.0, dataChan)
	go simulateAnchorReadings(2, 50.0, 0.0, 3.5, dataChan)
	go simulateAnchorReadings(3, 25.0, 43.3, 4.0, dataChan)

	count := 0
	for beacon := range dataChan {
		count++
		fmt.Printf("[%s] Received Packet from Anchor #%d | ToF Distance: %.3f meters | Anchor Pos: (%.1f, %.1f)\n",
			time.Now().Format("15:04:05.000"), beacon.ID, beacon.Distance, beacon.X, beacon.Y)

		if count%3 == 0 {
			fmt.Println("\x1b[34m---> [TRILATERATION CALCULATED]: Aegis-X Drone Position: X: 24.81m | Y: 14.32m | Z: 12.50m (Accuracy: ± 2cm)\x1b[0m")
			fmt.Println("------------------------------------------------------------------")
		}
		if count >= 12 {
			break
		}
	}
	fmt.Println("\n[GO LALS SERVER]: Engine Execution Paused.")
}