#!/usr/bin/env python3
"""Nim backend: link-output.json → Nim multi-file output.

Usage:
    python3 -m toolchain.emit.nim LINK_OUTPUT.json --output-dir out/nim/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from toolchain.emit.nim.emitter import transpile_to_nim_native
from toolchain.emit.loader import emit_all_modules


def _copy_runtime(output_dir: str) -> None:
    """Copy Nim runtime files into the output directory."""
    src_root = Path(__file__).resolve().parents[2] / "runtime" / "nim"
    out = Path(output_dir)
    specs = [
        ("built_in/py_runtime.nim", "py_runtime.nim"),
        ("generated/utils/image_runtime.nim", "image_runtime.nim"),
    ]
    for src_rel, dst_rel in specs:
        src = src_root / src_rel
        if not src.exists():
            continue
        dst = out / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.nim LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/nim"
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

    rc = emit_all_modules(input_path, output_dir, ".nim", transpile_to_nim_native)
    if rc != 0:
        return rc
    _copy_runtime(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
