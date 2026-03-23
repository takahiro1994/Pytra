# Native implementation of pytra.std.os for Nim.
#
# source: src/pytra/std/os.py

import std/os

proc getcwd*(): string = getCurrentDir()

proc mkdir*(p: string, exist_ok: bool = false): void = createDir(p)

proc makedirs*(p: string, exist_ok: bool = false): void =
  createDir(p)
