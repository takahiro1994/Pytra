"""C# backend CLI: manifest.json → C# multi-file output."""
from __future__ import annotations

import os
from pathlib import Path as NativePath

from pytra.std.pathlib import Path

from toolchain.emit.common.cli_runner import run_emit_cli
from toolchain.emit.cs.emitter import emit_cs_module


def _copy_cs_runtime(output_dir: Path) -> None:
    """Copy C# runtime files into the emit directory."""
    runtime_root_native = NativePath(__file__).resolve().parents[3] / "runtime" / "cs"
    if not runtime_root_native.exists():
        return
    built_in = runtime_root_native / "built_in" / "py_runtime.cs"
    if built_in.exists():
        dst = output_dir.joinpath("built_in").joinpath("py_runtime.cs")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(built_in.read_text(encoding="utf-8"), encoding="utf-8")
    std_dir = runtime_root_native / "std"
    if std_dir.exists():
        for name in os.listdir(std_dir):
            if not name.endswith(".cs"):
                continue
            cs_file = std_dir / name
            dst = output_dir.joinpath("std").joinpath(name)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(cs_file.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    import sys
    return run_emit_cli(emit_cs_module, sys.argv[1:], default_ext=".cs", post_emit=_copy_cs_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
