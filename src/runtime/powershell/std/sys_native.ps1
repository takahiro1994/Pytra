# sys_native.ps1 — native seam for pytra.std.sys

$script:argv = @()
$script:path = @()
$script:stderr = $null
$script:stdout = $null

function __native_get_argv { param() return $script:argv }
function __native_set_argv { param($values) $script:argv = @($values) }
function __native_get_path { param() return $script:path }
function __native_set_path { param($values) $script:path = @($values) }
function __native_exit { param($code = 0) [Environment]::Exit($code) }
function __native_write_stderr { param($text) [Console]::Error.Write($text) }
function __native_write_stdout { param($text) [Console]::Out.Write($text) }
