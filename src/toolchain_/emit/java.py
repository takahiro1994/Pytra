#!/usr/bin/env python3
"""Java backend: manifest.json → Java multi-file output.

Java requires filename == public class name, so the entry module logic is
emitted to {module_id}.java and a thin Main.java wrapper is generated
separately (spec-emitter-guide.md §5 "Java の main 分離").
"""

from __future__ import annotations

import sys
from pathlib import Path as NativePath
from typing import Any

from toolchain.emit.java.emitter import transpile_to_java
from toolchain.emit.java.emitter.java_native_emitter import _safe_ident
from toolchain.emit.loader import load_linked_modules, copy_native_runtime


def _is_extern_only(source: str) -> bool:
    """Check if generated source only contains _native delegations (no real logic)."""
    for line in source.splitlines():
        stripped = line.strip()
        if stripped == "" or stripped.startswith("//") or stripped.startswith("/*"):
            continue
        if stripped.startswith("public final class ") or stripped.startswith("private "):
            continue
        if stripped == "}" or stripped == "{":
            continue
        if "_native." in stripped or "return _native." in stripped:
            continue
        if stripped.startswith("public static "):
            continue
        return False
    return True


def _generate_main_java(body_class: str) -> str:
    """Generate a thin Main.java that delegates to the body class."""
    lines: list[str] = []
    lines.append("public final class Main {")
    lines.append("    public static void main(String[] args) {")
    lines.append("        " + body_class + "._case_main();")
    lines.append("    }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _emit_java_modules(input_path: str, output_dir: str) -> int:
    """Load linked modules and emit Java files.

    Entry module logic is emitted to {module_id}.java.
    A thin Main.java wrapper is generated separately.
    """
    modules, entry_modules = load_linked_modules(input_path)
    entry_set = set(entry_modules)
    out = NativePath(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for mod in modules:
        module_id: str = mod["module_id"]
        east_doc: dict[str, Any] = mod["east_doc"]
        is_entry: bool = mod.get("is_entry", False) or module_id in entry_set

        # built_in modules are provided by PyRuntime — skip emit (§6)
        if module_id.startswith("pytra.built_in."):
            continue

        # Inject emit_context
        meta = east_doc.get("meta")
        if not isinstance(meta, dict):
            meta = {}
            east_doc["meta"] = meta
        rel_module = module_id
        if rel_module.startswith("pytra."):
            rel_module = rel_module[len("pytra."):]
        rel_path = rel_module.replace(".", "/") + ".java"
        depth = rel_path.count("/")
        root_rel_prefix = "../" * depth if depth > 0 else "./"
        meta["emit_context"] = {
            "module_id": module_id,
            "root_rel_prefix": root_rel_prefix,
            "is_entry": bool(is_entry),
        }

        if is_entry:
            # Emit logic body to {module_id}.java (no main method)
            body_class = _safe_ident(module_id, "Module")
            source = transpile_to_java(east_doc, class_name=body_class, emit_main=False)
            if source == "":
                continue
            # Use module_id as filename (class is package-private, no name constraint)
            out_path = out / (module_id + ".java")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(source, encoding="utf-8")
            print("generated: " + str(out_path))

            # Generate thin Main.java
            main_source = _generate_main_java(body_class)
            main_path = out / "Main.java"
            main_path.write_text(main_source, encoding="utf-8")
            print("generated: " + str(main_path))
        else:
            try:
                source = transpile_to_java(east_doc)
            except RuntimeError:
                # Skip modules with unsupported constructs (e.g. union types)
                continue
            if source == "":
                continue
            # Skip @extern-only modules whose native file is missing
            native_check = rel_module.replace(".", "/") + "_native.java"
            if _is_extern_only(source) and not (out / native_check).exists():
                runtime_src = NativePath("src/runtime/java") / native_check
                if not runtime_src.exists():
                    continue
            out_path = out / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(source, encoding="utf-8")
            print("generated: " + str(out_path))

    return 0


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) == 0 or argv[0] in ("-h", "--help"):
        print("usage: toolchain.emit.java MANIFEST.json --output-dir DIR")
        return 0

    input_path = ""
    output_dir = "work/tmp/java"
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

    rc = _emit_java_modules(input_path, output_dir)
    if rc != 0:
        return rc
    copy_native_runtime(output_dir, "java")
    return 0


if __name__ == "__main__":
    sys.exit(main())
