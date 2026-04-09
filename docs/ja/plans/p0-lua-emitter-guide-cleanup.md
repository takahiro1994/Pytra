# P0-LUA-EMITTER-GUIDE-CLEANUP

## 背景

Lua emitter に emitter guide 違反が残っている。

- `typing` / `__future__` / `dataclasses` の import skip を emitter が直接ハードコードしている
- `pytra.built_in.*` の扱いを emitter が直接分岐している
- `pytra_isinstance` を emitter が直接生成していて、runtime protocol 実装を emitter が抱えている

これらは emitter guide の

- 具体的な module id / runtime protocol の emitter 直書き禁止
- skip / runtime wiring は mapping / loader / runtime 側へ寄せる

に反する。

## 目標

1. Lua emitter から concrete module id の直書きを外す
2. Lua emitter から `pytra_isinstance` 生成を外し、runtime 常設 helper に戻す
3. TODO と parity を更新して cleanup を完了化する

## 実施方針

### 1. import / module skip の直書き除去

- `ImportFrom` の `typing` / `__future__` / `dataclasses` 直判定を削除する
- built-in prefix の追加 skip 分岐を削除し、既存の `should_skip_module(...)` のみを使う

### 2. `pytra_isinstance` の runtime への移管

- `src/runtime/lua/built_in/py_runtime.lua` に `pytra_isinstance(obj, class_tbl)` を常設する
- `src/toolchain/emit/lua/emitter.py` から module header での helper 生成を削除する
- `pytra.built_in.type_id_table` 向けの特別な `pytra_isinstance(actual, tid)` 生成も削除する

### 3. ドキュメント更新

- `docs/ja/todo/lua.md` に cleanup タスクを追加し、同一コミットで完了化する
- 既存の `P0-LUA-TYPE-ID-CLEANUP` は「runtime helper 削除」前提から、guide cleanup 後の状態に合わせて注記を更新する

## 完了条件

- Lua emitter から `typing` / `dataclasses` / `__future__` import skip の直書きが消えている
- Lua emitter から `pytra.built_in.*` prefix の直書きが消えている
- Lua emitter が `pytra_isinstance` 本体を生成していない
- Lua parity 対象を再確認して TODO を完了化している
