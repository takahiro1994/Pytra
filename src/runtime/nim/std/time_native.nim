# Native implementation of pytra.std.time for Nim.
#
# This file is copied over the linker-generated time/east.nim at emit time.
#
# source: src/pytra/std/time.py

import std/times

proc perf_counter*(): float =
  epochTime()
