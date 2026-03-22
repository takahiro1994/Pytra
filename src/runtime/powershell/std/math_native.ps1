# math_native.ps1 — native seam for pytra.std.math

$__native_pi = [Math]::PI
$__native_e  = [Math]::E

function __native_sqrt   { param($x) return [Math]::Sqrt($x) }
function __native_sin    { param($x) return [Math]::Sin($x) }
function __native_cos    { param($x) return [Math]::Cos($x) }
function __native_tan    { param($x) return [Math]::Tan($x) }
function __native_asin   { param($x) return [Math]::Asin($x) }
function __native_acos   { param($x) return [Math]::Acos($x) }
function __native_atan   { param($x) return [Math]::Atan($x) }
function __native_atan2  { param($x, $y) return [Math]::Atan2($x, $y) }
function __native_exp    { param($x) return [Math]::Exp($x) }
function __native_log    { param($x) return [Math]::Log($x) }
function __native_log10  { param($x) return [Math]::Log10($x) }
function __native_log2   { param($x) return [Math]::Log($x, 2) }
function __native_fabs   { param($x) return [Math]::Abs($x) }
function __native_floor  { param($x) return [int][Math]::Floor($x) }
function __native_ceil   { param($x) return [int][Math]::Ceiling($x) }
function __native_pow    { param($x, $y) return [Math]::Pow($x, $y) }
function __native_round  { param($x, $n = 0) return [Math]::Round($x, $n) }
function __native_trunc  { param($x) return [int][Math]::Truncate($x) }
