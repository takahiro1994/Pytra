#!/usr/bin/env python3
"""CS backend: manifest.json → CS multi-file output."""

from __future__ import annotations
import sys

from toolchain.emit.cs.emitter.cs_emitter import transpile_to_csharp
from toolchain.emit.loader import emit_all_modules


def _module_id_to_class_name(module_id: str) -> str:
    """モジュール ID からユニークなクラス名を生成する。

    例: "time/east" → "PytraModule_time_east"
    """
    safe = module_id.replace(".", "_").replace("/", "_").replace("-", "_")
    return "PytraModule_" + safe


def _transpile_cs(east_doc: dict) -> str:
    """Wrapper to adapt transpile_to_csharp to the standard (dict) -> str signature."""
    meta = east_doc.get("meta", {})
    emit_ctx = meta.get("emit_context", {}) if isinstance(meta, dict) else {}
    is_entry = emit_ctx.get("is_entry", False) if isinstance(emit_ctx, dict) else False
    module_id = emit_ctx.get("module_id", "") if isinstance(emit_ctx, dict) else ""

    # §6: built_in モジュールは py_runtime が提供するため emit 不要
    if module_id.startswith("pytra.built_in."):
        return ""

    if is_entry:
        return transpile_to_csharp(east_doc, emit_main=True, class_name="Program")

    # For extern delegate modules (std/time, std/math, etc.), use the canonical
    # C# class name that entry modules reference (e.g. "time", "math").
    from toolchain.frontends.runtime_symbol_index import canonical_runtime_module_id
    canonical = canonical_runtime_module_id(module_id.replace(".east", ""))
    if canonical.startswith("pytra."):
        tail = canonical.split(".")[-1]
    else:
        tail = canonical.split(".")[-1] if "." in canonical else canonical
    class_name = tail if tail != "" else _module_id_to_class_name(module_id)
    return transpile_to_csharp(east_doc, emit_main=False, class_name=class_name)


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.cs MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/cs"
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

    return emit_all_modules(input_path, output_dir, ".cs", _transpile_cs, lang="cs")


if __name__ == "__main__":
    sys.exit(main())
