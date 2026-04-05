# png_native.ps1 — I/O adapter for pytra.utils.png
# The actual PNG encoding (CRC32/Adler32/DEFLATE) is compiled from src/pytra/utils/png.py

$__png_compiled = Join-Path $PSScriptRoot "../utils/png.ps1"
if (Test-Path $__png_compiled) { . $__png_compiled }
