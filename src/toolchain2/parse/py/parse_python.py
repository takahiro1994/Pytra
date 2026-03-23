"""Python frontend: .py → .py.east1

現行の toolchain.compile.core_entrypoints.convert_path を利用して
Python ソースを EAST1 (east_stage=1) に変換する。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_python_file(input_path: Path) -> dict[str, Any]:
    """.py ファイルを読み込み、EAST1 ドキュメント (east_stage=1) を返す。"""
    from toolchain.compile.core_entrypoints import convert_path as _convert_path
    from toolchain.compile.east1 import normalize_east1_root_document

    raw_east = _convert_path(input_path, parser_backend="self_hosted")
    return normalize_east1_root_document(raw_east)
