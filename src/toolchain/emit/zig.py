#!/usr/bin/env python3
"""Zig backend: manifest.json → Zig multi-file output."""

from __future__ import annotations

import sys
from pathlib import Path

from toolchain.emit.zig.emitter import transpile_to_zig_native
from toolchain.emit.loader import emit_all_modules

_RUNTIME_ROOT = Path(__file__).resolve().parents[2] / "runtime" / "zig"


def _has_native_file(module_id: str) -> bool:
    """Check if a _native.zig file exists for the given module_id."""
    rel = module_id
    if rel.startswith("pytra."):
        rel = rel[len("pytra."):]
    native_path = _RUNTIME_ROOT / (rel.replace(".", "/") + "_native.zig")
    return native_path.exists()


def _generate_native_reexport(module_id: str, root_rel_prefix: str) -> str:
    """Generate a thin re-export wrapper that delegates to the _native file."""
    rel = module_id
    if rel.startswith("pytra."):
        rel = rel[len("pytra."):]
    native_mod = rel.replace(".", "/") + "_native"
    native_name = native_mod.split("/")[-1]
    lines: list[str] = []
    lines.append("// Auto-generated re-export from " + native_name + ".zig")
    lines.append('const ' + native_name + ' = @import("' + root_rel_prefix + native_mod + '.zig");')
    lines.append("pub usingnamespace " + native_name + ";")
    lines.append("")
    return "\n".join(lines)


def _transpile_zig(east_doc: dict) -> str:
    meta = east_doc.get("meta", {})
    emit_ctx = meta.get("emit_context", {}) if isinstance(meta, dict) else {}
    is_entry = emit_ctx.get("is_entry", False) if isinstance(emit_ctx, dict) else False
    module_id = emit_ctx.get("module_id", "") if isinstance(emit_ctx, dict) else ""
    root_rel_prefix = emit_ctx.get("root_rel_prefix", "./") if isinstance(emit_ctx, dict) else "./"
    # If a _native.zig file exists for this module, generate a re-export wrapper
    # instead of transpiling the EAST3 (avoids PyObject type limitations).
    if module_id != "" and not is_entry and _has_native_file(module_id):
        return _generate_native_reexport(module_id, root_rel_prefix)
    return transpile_to_zig_native(east_doc, is_submodule=not is_entry)


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.zig MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/zig"
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

    return emit_all_modules(input_path, output_dir, ".zig", _transpile_zig, lang="zig")


if __name__ == "__main__":
    sys.exit(main())
