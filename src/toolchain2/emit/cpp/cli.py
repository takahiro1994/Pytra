"""C++ backend CLI: manifest.json → C++ multi-file output."""
from __future__ import annotations

from pytra.std.json import JsonVal
from pytra.std.pathlib import Path

from toolchain2.emit.common.cli_runner import run_emit_cli
from toolchain2.emit.cpp.runtime_bundle import write_helper_module_artifacts
from toolchain2.emit.cpp.runtime_bundle import write_runtime_module_artifacts
from toolchain2.emit.cpp.runtime_bundle import write_user_module_artifacts


def _helper_cpp_rel_path(module_id: str) -> str:
    if module_id.startswith("pytra."):
        return module_id[len("pytra."):].replace(".", "/")
    return module_id.replace(".", "/")


def _emit_cpp_direct(east_doc: dict[str, JsonVal], output_dir: Path) -> int:
    """Emit C++ files directly. Handles module_kind branching internally."""
    meta: JsonVal = east_doc.get("meta")
    module_id: str = ""
    module_kind: str = ""
    source_path: str = ""
    if isinstance(meta, dict):
        mid: JsonVal = meta.get("_cli_module_id")
        if isinstance(mid, str):
            module_id = mid
        mk: JsonVal = meta.get("_cli_module_kind")
        if isinstance(mk, str):
            module_kind = mk
        sp: JsonVal = meta.get("_cli_source_path")
        if isinstance(sp, str):
            source_path = sp
    if module_kind == "runtime":
        return write_runtime_module_artifacts(
            module_id,
            east_doc,
            output_dir=output_dir,
            source_path=source_path,
        )
    if module_kind == "helper":
        rel_header_path: str = _helper_cpp_rel_path(module_id) + ".h"
        return write_helper_module_artifacts(
            module_id,
            east_doc,
            output_dir=output_dir,
            rel_header_path=rel_header_path,
        )
    return write_user_module_artifacts(
        module_id,
        east_doc,
        output_dir=output_dir,
    )


def main() -> int:
    import sys
    return run_emit_cli(argv=sys.argv[1:], direct_emit_fn=_emit_cpp_direct)


if __name__ == "__main__":
    raise SystemExit(main())
