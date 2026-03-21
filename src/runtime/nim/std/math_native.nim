# Native implementation of pytra.std.math for Nim.
#
# This file is copied over the linker-generated math/east.nim at emit time.
# The generated module body references the Python `math` module which is
# invalid in Nim; this native seam delegates to Nim's std/math.
#
# source: src/pytra/std/math.py

import std/math

let pi* = PI
let e* = E

proc sqrt*(x: float): float = math.sqrt(x)
proc sin*(x: float): float = math.sin(x)
proc cos*(x: float): float = math.cos(x)
proc tan*(x: float): float = math.tan(x)
proc exp*(x: float): float = math.exp(x)
proc log*(x: float): float = math.ln(x)
proc log10*(x: float): float = math.log10(x)
proc fabs*(x: float): float = abs(x)
proc floor*(x: float): float = math.floor(x)
proc ceil*(x: float): float = math.ceil(x)
proc pow*(x: float, y: float): float = math.pow(x, y)
