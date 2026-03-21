#!/usr/bin/env python3
"""PHP backend: link-output.json → PHP multi-file output.

Usage:
    python3 -m toolchain.emit.php LINK_OUTPUT.json --output-dir out/php/
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from toolchain.emit.php.emitter import transpile_to_php_native
from toolchain.emit.loader import emit_all_modules


def _copy_runtime(output_dir: str) -> None:
    """Copy PHP runtime files into a pytra/ subdirectory of output_dir."""
    src_root = Path(__file__).resolve().parents[2] / "runtime" / "php"
    dst_root = Path(output_dir) / "pytra"
    specs = [
        ("built_in/py_runtime.php", "py_runtime.php"),
        ("std/math_native.php", "std/math_native.php"),
        ("std/time_native.php", "std/time_native.php"),
    ]
    for src_rel, dst_rel in specs:
        src = src_root / src_rel
        if not src.exists():
            continue
        dst = dst_root / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))


def _overlay_native_std(output_dir: str) -> None:
    """Overwrite linker-generated std modules with native implementations.

    The linker emits math/east.php and time/east.php from the EAST IR, but
    their function bodies reference the Python stdlib (e.g. ``$math->sqrt``)
    which is invalid in PHP.  Native seam files provide correct
    implementations that delegate to PHP built-in functions.
    """
    src_root = Path(__file__).resolve().parents[2] / "runtime" / "php"
    out = Path(output_dir)
    overlays = [
        ("std/math_native.php", "math/east.php"),
        ("std/time_native.php", "time/east.php"),
    ]
    for src_rel, dst_rel in overlays:
        src = src_root / src_rel
        dst = out / dst_rel
        if src.exists() and dst.exists():
            shutil.copy2(str(src), str(dst))


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.php LINK_OUTPUT.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "out/php"
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

    rc = emit_all_modules(input_path, output_dir, ".php", transpile_to_php_native)
    if rc != 0:
        return rc
    _copy_runtime(output_dir)
    _overlay_native_std(output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
