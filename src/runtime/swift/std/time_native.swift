// Generated std/time.swift delegates host bindings through this native seam.

#if canImport(Darwin)
import Foundation
func time_native_perf_counter() -> Double {
    return CFAbsoluteTimeGetCurrent()
}
#else
import Glibc
private func _time_native_clock_nsec() -> UInt64 {
    var ts = timespec()
    clock_gettime(CLOCK_MONOTONIC, &ts)
    return UInt64(ts.tv_sec) &* 1_000_000_000 &+ UInt64(ts.tv_nsec)
}
func time_native_perf_counter() -> Double {
    return Double(_time_native_clock_nsec()) / 1_000_000_000.0
}
#endif
