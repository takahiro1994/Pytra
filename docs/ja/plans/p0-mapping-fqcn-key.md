# P0-MAPPING-FQCN-KEY: mapping.json の calls キーを完全修飾に統一する

最終更新: 2026-04-03

## 背景

mapping.json の `calls` キーが bare symbol（`"sin"`, `"cos"` 等）になっている。`resolve_runtime_symbol_name`（`src/toolchain2/emit/common/code_emitter.py`）が `runtime_symbol` の値だけで mapping.json を引いているため。

これは名前衝突のリスクがある。ユーザーが `def sin(x):` を定義したら、mapping.json の `"sin": "std::sin"` にヒットして `std::sin` に変換されてしまう。

EAST3 は `runtime_module_id: "pytra.std.math"` + `runtime_symbol: "sin"` と完全修飾の情報を持っている。mapping.json のキーも完全修飾（`"pytra.std.math.sin": "std::sin"`）にすべき。

### 現状の問題

1. **名前衝突**: bare `"sin"` はユーザー定義関数と衝突しうる
2. **重複エントリ**: `"math.sin"` と `"sin"` の両方が登録されている（旧 `builtin_name` 対応の名残）
3. **死んだエントリ**: `"math.sin"` は EAST3 の `runtime_call` としても `runtime_symbol` としても使われない
4. **lint 誤検出**: `rt: call_cov` が mapping.json のキーと EAST3 の `runtime_call` を突き合わせて大量の未一致を報告

### 影響箇所

- `src/toolchain2/emit/common/code_emitter.py` — `resolve_runtime_symbol_name` と `collect_runtime_symbol_imports` の解決ロジック
- 全18言語の `src/runtime/<lang>/mapping.json` — `calls` キーの書き換え
- `tools/check/check_runtime_call_coverage.py` — 突き合わせロジック

## 方針

1. `resolve_runtime_symbol_name` に `runtime_module_id` を渡す
2. 完全修飾キー（`runtime_module_id + "." + runtime_symbol`）で mapping.json を先に引く
3. fallback として bare symbol でも引く（移行期間中の互換）
4. 全言語の mapping.json キーを完全修飾に統一
5. fallback を削除して完全修飾のみにする

## サブタスク

1. [ ] [ID: P0-FQCN-KEY-S1] `resolve_runtime_symbol_name` に `module_id` パラメータを追加し、`module_id + "." + symbol` で先に引くようにする（bare fallback は残す）
2. [ ] [ID: P0-FQCN-KEY-S2] 全言語の mapping.json `calls` キーを完全修飾（`pytra.std.math.sin` 等）に統一する。重複エントリ（`"math.sin"` + `"sin"`）を完全修飾 1 エントリに統合
3. [ ] [ID: P0-FQCN-KEY-S3] bare fallback を削除し、完全修飾のみで解決する
4. [ ] [ID: P0-FQCN-KEY-S4] `check_runtime_call_coverage.py` の突き合わせロジックを完全修飾に対応させる
5. [ ] [ID: P0-FQCN-KEY-S5] C++ parity に回帰がないことを確認する（C++ で代表確認。各言語は各担当に委譲）

## 決定ログ

- 2026-04-03: mapping.json の `"sin"` が bare symbol でユーザー定義関数と衝突するリスクを指摘。EAST3 は `runtime_module_id` + `runtime_symbol` を完全修飾で持っているので、mapping.json キーも完全修飾にすべき。共通基盤（`code_emitter.py`）のバグとして起票。
