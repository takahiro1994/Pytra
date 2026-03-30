<a href="../../en/todo/infra.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — インフラ・ツール・仕様

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-30（P0-SELFHOST-GOLDEN-UNIFIED S1-S2 完了）

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。

完了済みタスクは [アーカイブ](archive/20260330.md) / [P10-REORG アーカイブ](archive/20260330-p10reorg.md) を参照。

## 未完了タスク

### P0-SELFHOST-MATRIX-AUTO-REFRESH: parity check 末尾で selfhost マトリクスを自動再集約する

1. [ ] [ID: P0-SELFHOST-REFRESH-S1] parity check（fast 版）の末尾に `_maybe_refresh_selfhost_python()` を追加する — `selfhost_python.json` の mtime が 30 分以上古ければ `run_selfhost_parity.py --selfhost-lang python` を自動実行して `.parity-results/selfhost_python.json` を再集約する
2. [ ] [ID: P0-SELFHOST-REFRESH-S2] 再集約後に `gen_backend_progress.py` が selfhost マトリクスに反映することを確認する（既存の `_maybe_regenerate_progress` の 10 分ルールで自動実行される）

### P10-STDLIB-TEST-SEPARATION: stdlib テストを fixture から分離し、モジュール別マトリクスを生成する

文脈: [docs/ja/plans/p10-stdlib-test-separation.md](../plans/p10-stdlib-test-separation.md)

1. [ ] [ID: P10-STDLIB-S1] `test/stdlib/source/py/` を新設し、モジュールごとのフォルダ（`math/`, `json/`, `pathlib/`, `re/`, `argparse/`, `sys/`, `os/`, `dataclasses/`, `enum/`, `typing/`）を作成する
2. [ ] [ID: P10-STDLIB-S2] `test/fixture/source/py/stdlib/` の既存テストを `test/stdlib/source/py/<module>/` に移動する
3. [ ] [ID: P10-STDLIB-S3] parity check に `--case-root stdlib` を追加する。`.parity-results/<lang>_stdlib.json` に結果を蓄積する
4. [ ] [ID: P10-STDLIB-S4] `gen_backend_progress.py` にモジュール × 言語のマトリクス生成を追加する。出力先: `docs/ja/progress/backend-progress-stdlib.md`（日英同時生成）
5. [ ] [ID: P10-STDLIB-S5] `progress/index.md` に stdlib マトリクスへのリンクを追加する
6. [ ] [ID: P10-STDLIB-S6] fixture の golden を再生成し、移動した stdlib テストが fixture マトリクスから消えていることを確認する

（P20-INT32 は [plans/p4-int32-default.md](../plans/p4-int32-default.md) に保留中。再開時にここへ戻す。）
