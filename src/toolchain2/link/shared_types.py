"""Shared link-stage dataclasses.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from dataclasses import dataclass

from pytra.std.json import JsonVal


@dataclass
class LinkedModule:
    """1 module の linked 結果。"""
    module_id: str
    input_path: str
    source_path: str
    is_entry: bool
    east_doc: dict[str, JsonVal]
    module_kind: str  # "user" | "runtime" | "helper"
