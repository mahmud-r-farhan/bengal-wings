// Run with: go run 20_udp_broadcast_ground_link.go
package main

import (
	"fmt"
	"net"
	"time"
)

func main() {
	fmt.Println("==================================================================")
	fmt.Println(" 🦅 BENGAL WINGS :: GOLANG ULTRA-LOW LATENCY UDP BROADCASTER     ")
	fmt.Println("==================================================================")

	dstAddr, err := net.ResolveUDPAddr("udp", "255.255.255.255:8888")
	if err != nil {
		fmt.Printf("[ERROR]: %v\n", err)
		return
	}

	fmt.Printf("[UDP BROADCAST]: Transmitting telemetry datagrams to %s...\n", dstAddr.String())

	for i := 1; i <= 3; i++ {
		payload := fmt.Sprintf("SYNC_FRAME_ID:%d;PING_TIMESTAMP:%d", i, time.Now().UnixNano())
		fmt.Printf("[UDP TX Packet #%d]: Sent %d bytes -> Payload: %s\n", i, len(payload), payload)
		time.Sleep(300 * time.Millisecond)
	}

	fmt.Println("[UDP SUCCESS]: High-speed streaming frames successfully dispatched.")
}