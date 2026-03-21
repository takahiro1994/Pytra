#!/usr/bin/env python3
"""Standalone LUA backend: EAST3 JSON → LUA source.

Usage:
    python3 -m toolchain.emit.lua INPUT.json -o out/output.lua
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from toolchain.emit.lua.emitter import transpile_to_lua_native


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.lua INPUT.json -o OUTPUT.lua")
        return 0

    input_path = ""
    output_path = ""
    i = 0
    while i < len(argv):
        tok = argv[i]
        if (tok == "-o" or tok == "--output") and i + 1 < len(argv):
            output_path = argv[i + 1]
            i += 2
            continue
        if not tok.startswith("-") and input_path == "":
            input_path = tok
        i += 1

    if input_path == "":
        print("error: input file is required", file=sys.stderr)
        return 1
    if output_path == "":
        output_path = Path(input_path).stem + ".lua"

    east_doc = json.loads(Path(input_path).read_text(encoding="utf-8"))
    source = transpile_to_lua_native(east_doc)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(source, encoding="utf-8")
    print("generated: " + output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
