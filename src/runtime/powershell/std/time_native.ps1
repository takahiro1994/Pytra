# time_native.ps1 — native seam for pytra.std.time

function __native_perf_counter {
    param()
    return [double]([System.Diagnostics.Stopwatch]::GetTimestamp()) / [double]([System.Diagnostics.Stopwatch]::Frequency)
}
