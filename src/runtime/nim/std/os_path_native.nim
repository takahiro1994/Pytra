# Native implementation of pytra.std.os_path for Nim.
#
# source: src/pytra/std/os_path.py

import std/os
import std/strutils

proc join*(a: string, b: string): string = joinPath(a, b)

proc dirname*(p: string): string = parentDir(p)

proc basename*(p: string): string = extractFilename(p)

proc splitext*(p: string): (string, string) =
  let (dir, name, ext) = splitFile(p)
  result = (joinPath(dir, name), ext)

proc abspath*(p: string): string = absolutePath(p)

proc exists*(p: string): bool = fileExists(p) or dirExists(p)
