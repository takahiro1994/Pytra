# Native implementation of pytra.std.math for Nim.
#
# Provides Python math module API delegating to Nim's std/math.
# Function names match the Python originals exactly (§5.1).
#
# source: src/pytra/std/math.py

from std/math import nil

let pi*: float = math.PI
let e*: float = math.E

proc sqrt*(x: float): float = math.sqrt(x)
proc sin*(x: float): float = math.sin(x)
proc cos*(x: float): float = math.cos(x)
proc tan*(x: float): float = math.tan(x)
proc exp*(x: float): float = math.exp(x)
proc log*(x: float): float = math.ln(x)
proc log10*(x: float): float = math.log10(x)
proc fabs*(x: float): float =
  if x < 0.0: -x else: x
proc floor*(x: float): float = math.floor(x)
proc ceil*(x: float): float = math.ceil(x)
proc pow*(x: float, y: float): float = math.pow(x, y)
