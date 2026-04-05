# os_native.ps1 — native seam for pytra.std.os

$__os_path_seam = Join-Path $PSScriptRoot "os_path_native.ps1"
if (Test-Path $__os_path_seam) { . $__os_path_seam }

function __native_getcwd { param() return (Get-Location).Path }
function __native_mkdir { param($p) New-Item -ItemType Directory -Path $p -Force | Out-Null }
function __native_makedirs { param($p, $exist_ok = $false) if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null } }
function __native_listdir { param($p = ".") return @(Get-ChildItem -Path $p -Name) }
