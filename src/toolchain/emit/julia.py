#!/usr/bin/env python3
"""Julia backend: link-output.json → Julia multi-file output.

Usage:
    python3 -m toolchain.emit.julia LINK_OUTPUT.json --output-dir out/julia/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from toolchain.emit.julia.emitter import transpile_to_julia_native
from toolchain.emit.loader import emit_all_modules


def _copy_runtime(output_dir: str) -> None:
    """Copy py_runtime.jl to each directory containing generated .jl files."""
    src_dir = Path(__file__).resolve().parent.parent.parent
    runtime_src = src_dir / "runtime" / "julia" / "built_in" / "py_runtime.jl"
    if not runtime_src.exists():
        return
    out = Path(output_dir)
    # Copy runtime to all directories containing .jl files
    dirs_seen: set[str] = set()
    for jl_file in out.rglob("*.jl"):
        parent = str(jl_file.parent)
        if parent not in dirs_seen:
            dirs_seen.add(parent)
            dest = jl_file.parent / "py_runtime.jl"
            if not dest.exists():
                shutil.copy2(str(runtime_src), str(dest))


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.julia LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/julia"
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

    rc = emit_all_modules(input_path, output_dir, ".jl", transpile_to_julia_native)
    if rc == 0:
        _copy_runtime(output_dir)
    return rc


if __name__ == "__main__":
    sys.exit(main())
