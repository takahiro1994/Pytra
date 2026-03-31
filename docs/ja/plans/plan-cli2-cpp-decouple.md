# 計画: pytra-cli2.py から C++ 固有 import を分離 (P0-CLI2-CPP-DECOUPLE)

## 背景

`pytra-cli2.py` が top-level で `toolchain2.emit.cpp.runtime_bundle` を import しているため、Rust / Go 等の selfhost で全言語の emitter モジュールが依存グラフに入り、cargo build / go build が不要なモジュールのコンパイルエラーで失敗する。

`pytra-cli2.py` は言語非依存のパイプライン入口であるべきで、C++ 固有の import が top-level にあるのは設計違反。

## 現状

```python
# pytra-cli2.py の top-level import
from toolchain2.emit.cpp.runtime_bundle import write_helper_module_artifacts
from toolchain2.emit.cpp.runtime_bundle import write_runtime_module_artifacts
from toolchain2.emit.cpp.runtime_bundle import write_user_module_artifacts
```

使用箇所は `_emit_cpp_linked_module()` 関数のみ（264〜285行目）。この関数は `-emit` / `-build` コマンドの C++ パスでしか呼ばれない。

## 設計

### 方針

`_emit_cpp_linked_module()` を `toolchain2.emit.cpp` 側に移し、`pytra-cli2.py` からは言語非依存の API で呼び出す。

### 具体的な変更

1. `toolchain2.emit.cpp.cli` (または `toolchain2.emit.cpp.emit_linked`) に `emit_cpp_linked_module(module, output_dir)` を新設
2. `pytra-cli2.py` から `_emit_cpp_linked_module()` と `from toolchain2.emit.cpp.runtime_bundle import ...` の 3行を削除
3. `pytra-cli2.py` の `-emit` / `-build` の C++ パスで、言語ディスパッチテーブル経由で呼び出す

### 言語ディスパッチの形

```python
# pytra-cli2.py — 言語非依存
def _emit_linked_module(target: str, module: LinkedModule, output_dir: Path) -> int:
    if target == "cpp":
        from toolchain2.emit.cpp.emit_linked import emit_cpp_linked_module
        return emit_cpp_linked_module(module, output_dir)
    # 他言語は既存パス
    ...
```

ただし spec-agent.md §5 で動的 import は selfhost 対象コードでは禁止。なので:

**選択肢 A**: `_emit_linked_module` をモジュールレベル関数テーブル（dict）にし、各言語 emitter が起動時に登録する

**選択肢 B**: `pytra-cli2.py` の `-build` コマンド自体を言語別のサブコマンドに分離し、C++ build は `toolchain2.emit.cpp.cli` が担当する。`pytra-cli2.py` は `-build` 時にサブプロセスで言語別 CLI を呼ぶ

**選択肢 C**: selfhost 対象を `pytra-cli2.py` 全体ではなく、言語非依存部分のみにする。C++ 固有パスは selfhost 対象外として明示する

**推奨**: 選択肢 B。`pytra-cli.py`（旧 CLI）が既に C++ build を `toolchain2.emit.cpp.cli` にサブプロセス委譲しているので、`pytra-cli2.py` も同じ構造にする。

## 影響範囲

- `pytra-cli2.py` の import が減る（C++ 依存が消える）
- C++ の `-build` の動作は変わらない（内部構造のリファクタのみ）
- Rust / Go の selfhost で C++ emitter がグラフに入らなくなる
- fixture + sample parity の全言語確認が必要
