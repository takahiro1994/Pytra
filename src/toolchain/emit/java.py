#!/usr/bin/env python3
"""Java backend: link-output.json → Java multi-file output.

Usage:
    python3 -m toolchain.emit.java LINK_OUTPUT.json --output-dir out/java/
"""

from __future__ import annotations

import sys

from toolchain.emit.java.emitter import transpile_to_java
from toolchain.emit.loader import emit_all_modules


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.java LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/java"
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
        print("error: input link-output.json is required", file=sys.stderr)
        return 1

    return emit_all_modules(input_path, output_dir, ".java", transpile_to_java)


if __name__ == "__main__":
    sys.exit(main())
