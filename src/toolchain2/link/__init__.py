"""toolchain2/link: east3-opt → linked east3 + manifest.

責務:
- multi-module 結合（import graph 解決、runtime module 追加）
- type_id テーブル生成
- call graph / SCC 構築
- dependency table 構築
- linked_program_v1 metadata 付与
- manifest.json (link-output.v1) 生成

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
"""

from __future__ import annotations

from toolchain2.link.linker import link_modules
from toolchain2.link.linker import LinkResult

__all__ = ["link_modules", "LinkResult"]
