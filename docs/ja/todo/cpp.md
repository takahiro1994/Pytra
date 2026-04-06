<a href="../../en/todo/cpp.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — C++ backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-04-06

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 未完了タスク

### P0-CPP-WITH: with 文を __enter__ / __exit__ プロトコルで実装する

文脈: [docs/ja/plans/p0-with-context-manager.md](../plans/p0-with-context-manager.md)

`With` ノードを context manager プロトコル（`__enter__` / `__exit__`）として正しく変換する。CommonRenderer にデフォルトの try/finally + hoist 変換を実装し、C++ emitter はそれを利用する。`PyFile` 廃止と `io.*` 型定義も含む。

Phase 1〜2 はインフラ（resolve/compile/CommonRenderer）修正、Phase 3 は `PyFile` 廃止、Phase 4 は parity 確認。

1. [x] [ID: P0-CPP-WITH-S1] resolve が `With` の `context_expr` に `__enter__` / `__exit__` の解決済み情報（`runtime_call` 等）を metadata として付与する
   完了メモ: `resolver.py` が `with_enter_*` / `with_exit_*` metadata と `with_enter_type` を付与するよう修正。`built_in/io.py` を registry に載せて `open()` / user-defined context manager の両方で解決する。
2. [x] [ID: P0-CPP-WITH-S2] CommonRenderer に `With` のデフォルト変換（try/finally + hoist）を実装する
   完了メモ: `common_renderer.py` に `With` の try/finally + hoist lowering を追加。C++ 側はそのデフォルトを使い、self-return nominal context だけ body 内参照束縛で alias を維持する。
3. [x] [ID: P0-CPP-WITH-S3] resolver の `open()` ハードコードを修正し、mode 引数に応じて `TextIOWrapper` / `BufferedWriter` / `BufferedReader` を返すようにする（`src/pytra/built_in/io.py` は定義済み）
   完了メモ: `open()` は mode リテラルに応じて `TextIOWrapper` / `BufferedWriter` / `BufferedReader`、不明時は `IOBase` を返す。C++ type map は runtime 実体の `PyFile` に正規化。
4. [x] [ID: P0-CPP-WITH-S4] resolver の `PyFile` メソッドハードコードを削除し、`built_in/io.py` から型を解決するように修正する。EAST3 golden を再生成する
   完了メモ: `PyFile` 特例を resolver から除去。`src/runtime/east/utils/assertions.east` を current runtime surface に合わせて更新し、`TextIOWrapper` / `Buffered*` の `__enter__` 正本も追加。
5. [x] [ID: P0-CPP-WITH-S5] `with_context_manager` + `with_statement` fixture で C++ parity PASS を確認する
   完了メモ: `python3 tools/check/runtime_parity_check_fast.py --case-root fixture --targets cpp with_context_manager with_statement` で `2/2 PASS`。`pathlib_extended:cpp`、`check_runtime_call_coverage.py --lang cpp --direction mapping-to-east`、`check_emitter_hardcode_lint.py --lang cpp` も確認済み。

### P20-CPP-SELFHOST: C++ emitter で toolchain2 を C++ に変換し g++ build を通す

文脈: [docs/ja/plans/p4-cpp-selfhost.md](../plans/p4-cpp-selfhost.md)

S0〜S4 完了済み（[archive/20260402.md](archive/20260402.md) 参照）。

1. [ ] [ID: P20-CPP-SELFHOST-S5] selfhost C++ バイナリを g++ でビルドし、リンクが通ることを確認する
2. [ ] [ID: P20-CPP-SELFHOST-S6] `run_selfhost_parity.py --selfhost-lang cpp --emit-target cpp --case-root fixture` で fixture parity が PASS することを確認する
3. [ ] [ID: P20-CPP-SELFHOST-S7] `run_selfhost_parity.py --selfhost-lang cpp --emit-target cpp --case-root sample` で sample parity が PASS することを確認する
