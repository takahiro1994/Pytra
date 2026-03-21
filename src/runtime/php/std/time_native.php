<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.time for PHP.
 *
 * This file is copied over the linker-generated time/east.php at emit time.
 *
 * source: src/pytra/std/time.py
 */

if (!function_exists('perf_counter')) {
    function perf_counter(): float {
        return microtime(true);
    }
}
