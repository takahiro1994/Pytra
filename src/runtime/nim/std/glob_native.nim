# Native implementation of pytra.std.glob for Nim.
#
# source: src/pytra/std/glob.py

import std/os

proc glob*(pattern: string): seq[string] =
  result = @[]
  for path in walkPattern(pattern):
    result.add(path)
