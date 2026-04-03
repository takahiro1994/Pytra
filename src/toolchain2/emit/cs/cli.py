"""C# backend CLI: manifest.json → C# multi-file output."""
from __future__ import annotations

from pytra.std.pathlib import Path

from toolchain2.emit.common.cli_runner import run_emit_cli
from toolchain2.emit.cs.emitter import emit_cs_module


def _copy_cs_runtime(output_dir: Path) -> None:
    """Copy C# runtime files into the emit directory."""
    runtime_root = Path(".").resolve().joinpath("src").joinpath("runtime").joinpath("cs")
    if not runtime_root.exists():
        return
    built_in = runtime_root.joinpath("built_in").joinpath("py_runtime.cs")
    if built_in.exists():
        dst = output_dir.joinpath("built_in").joinpath("py_runtime.cs")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(built_in.read_text(encoding="utf-8"), encoding="utf-8")
    std_dir = runtime_root.joinpath("std")
    if std_dir.exists():
        for cs_file in std_dir.glob("*.cs"):
            dst2 = output_dir.joinpath("std").joinpath(cs_file.name)
            dst2.parent.mkdir(parents=True, exist_ok=True)
            dst2.write_text(cs_file.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    import sys
    return run_emit_cli(emit_cs_module, sys.argv[1:], default_ext=".cs", post_emit=_copy_cs_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
