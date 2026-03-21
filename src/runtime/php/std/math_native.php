<?php
declare(strict_types=1);
/**
 * Native implementation of pytra.std.math for PHP.
 *
 * This file is copied over the linker-generated math/east.php at emit time.
 * The generated module body references the Python `math` module which is
 * invalid in PHP; this native seam delegates to PHP built-in functions.
 *
 * Function/variable names match the EAST module exports so that callers
 * resolved by the linker (`sqrt($x)`, `pi`, etc.) work directly.
 *
 * source: src/pytra/std/math.py
 */

if (!defined('pi')) { define('pi', M_PI); }
if (!defined('e'))  { define('e',  M_E);  }

// PHP built-in: sqrt, sin, cos, tan, exp, log, log10, floor, ceil, pow
// are already available as global functions.

// fabs is not a PHP built-in; delegate to abs().
if (!function_exists('fabs')) {
    function fabs($x) { return abs((float)$x); }
}
