// Zig native implementation for pytra.std.time
// source: src/runtime/zig/std/time_native.zig
const std = @import("std");

/// time.perf_counter() — seconds since arbitrary epoch (nanosecond precision).
pub fn perf_counter() f64 {
    const ns = std.time.nanoTimestamp();
    return @as(f64, @floatFromInt(ns)) / 1_000_000_000.0;
}
