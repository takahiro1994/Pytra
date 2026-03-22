#!/usr/bin/env python3
"""RS backend: manifest.json → RS multi-file output."""

from __future__ import annotations
import sys

from toolchain.emit.rs.emitter.rs_emitter import transpile_to_rust
from toolchain.emit.loader import emit_all_modules


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.rs MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/rs"
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

    return emit_all_modules(input_path, output_dir, ".rs", transpile_to_rust, lang="rs")


if __name__ == "__main__":
    sys.exit(main())
