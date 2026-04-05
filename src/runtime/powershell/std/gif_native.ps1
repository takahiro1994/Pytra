# gif_native.ps1 — I/O adapter for pytra.utils.gif
# The actual GIF encoding (LZW/palette) is compiled from src/pytra/utils/gif.py

$__gif_compiled = Join-Path $PSScriptRoot "../utils/gif.ps1"
if (Test-Path $__gif_compiled) { . $__gif_compiled }
