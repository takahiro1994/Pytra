#!/usr/bin/env python3
"""TS backend: manifest.json → TS multi-file output.

Usage:
    python3 -m toolchain.emit.ts MANIFEST.json --output-dir out/ts/
"""

from __future__ import annotations

import sys

from toolchain.emit.ts.emitter.ts_emitter import transpile_to_typescript
from toolchain.emit.loader import emit_all_modules
from toolchain.misc.js_runtime_shims import write_js_runtime_shims


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.ts MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/ts"
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--output-dir" and i + 1 < len(argv):
            output_dir = argv[i + 1]
            i += 2
            continue
        if not tok.startswith("-") and input_path == "":
            input_path = tok
        i += 1

    if input_path == "":
        print("error: input manifest.json is required", file=sys.stderr)
        return 1

    rc = emit_all_modules(input_path, output_dir, ".ts", transpile_to_typescript, lang="ts")
    if rc != 0:
        return rc
    from pytra.std.pathlib import Path as PytraPath
    write_js_runtime_shims(PytraPath(output_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
