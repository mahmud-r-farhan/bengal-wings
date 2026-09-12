// Run with: zig run 09_low_level_memory_allocator.zig
const std = @import("std");

const SensorReading = struct {
    timestamp: u64,
    distance_cm: u16,
    signal_quality: u8,
};

pub fn main() !void {
    const stdout = std.io.getStdOut().writer();

    try stdout.print("==================================================================\n", .{});
    try stdout.print(" 🦅 BENGAL WINGS :: ZIG LOW-LATENCY SENSOR RING BUFFER           \n", .{});
    try stdout.print("==================================================================\n", .{});

    var ring_buffer: [4]SensorReading = undefined;

    // Fill ring buffer with zero dynamic memory allocation overhead
    inline for (0..4) |idx| {
        ring_buffer[idx] = SensorReading{
            .timestamp = 1000 + idx * 50,
            .distance_cm = @intCast(150 + idx * 25),
            .signal_quality = 98,
        };
    }

    for (ring_buffer, 0..) |item, i| {
        try stdout.print("[BUFFER SLOT {d}] Time: {d}ms | LiDAR Reading: {d} cm | Quality: {d}%\n", .{ i, item.timestamp, item.distance_cm, item.signal_quality });
    }
    
    try stdout.print("\n[ZIG CORE]: Dynamic Memory Allocated: 0 Bytes (Zero Allocation Passed).\n", .{});
}