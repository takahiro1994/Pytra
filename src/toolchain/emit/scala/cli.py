"""Scala backend CLI: manifest.json → Scala multi-file output."""
from __future__ import annotations

from pytra.std.pathlib import Path

from toolchain.emit.common.cli_runner import run_emit_cli
from toolchain.emit.scala.emitter import emit_scala_module


def _copy_scala_runtime(output_dir: Path) -> None:
    """Copy Scala runtime files into the emit directory."""
    runtime_root = Path(".").resolve().joinpath("src").joinpath("runtime").joinpath("scala")
    if not runtime_root.exists():
        return
    for bucket in ["built_in", "std"]:
        bucket_dir = runtime_root.joinpath(bucket)
        if not bucket_dir.exists():
            continue
        for scala_file in bucket_dir.glob("*.scala"):
            dst = output_dir.joinpath(scala_file.name)
            dst.write_text(scala_file.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    import sys
    return run_emit_cli(emit_scala_module, sys.argv[1:], default_ext=".scala", post_emit=_copy_scala_runtime)


if __name__ == "__main__":
    raise SystemExit(main())
