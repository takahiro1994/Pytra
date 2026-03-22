# sys_native.ps1 — native seam for pytra.std.sys

$__native_argv = @()
$__native_path = @()
$__native_stderr = $null
$__native_stdout = $null

function __native_get_argv { param() return $script:__native_argv }
function __native_set_argv { param($values) $script:__native_argv = @($values) }
function __native_get_path { param() return $script:__native_path }
function __native_set_path { param($values) $script:__native_path = @($values) }
function __native_exit { param($code = 0) [Environment]::Exit($code) }
function __native_write_stderr { param($text) [Console]::Error.Write($text) }
function __native_write_stdout { param($text) [Console]::Out.Write($text) }
