<a href="../../en/plans/p6-go-selfhost.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P6-GO-SELFHOST: Go emitter で toolchain2 を Go に変換し go build を通す

最終更新: 2026-03-30
ステータス: 進行中（S1-S2 完了）

## 背景

Pytra の変換器自身（toolchain2）を Go に変換し、変換後の Go コンパイラが正しく動作することを検証する。Go は fixture + sample 全件 PASS 済みなので、selfhost に着手できる状態。

## フロー

1. `pytra-cli2 -build --target go` で toolchain2 全 `.py` を Go に変換
2. `go build` でコンパイルしてバイナリを生成
3. バイナリで fixture/sample/stdlib を変換し、Python と同じ出力が得られるか検証（P3-SELFHOST-PARITY の `run_selfhost_parity.py`）

## サブタスク

1. [S0] selfhost 対象コードの型注釈補完（他言語と共通）
2. [S1] toolchain2 → Go emit + go build 通過 ✅
3. [S2] build 失敗の emitter/runtime 修正 ✅
4. [S3] selfhost 用 Go golden 配置 + 回帰テスト（`regenerate_selfhost_golden.py --target go`）

## 設計判断

- EAST の workaround 禁止。build 失敗は emitter/runtime の修正で解消する
- 型注釈補完（S0）は他言語の selfhost と共有。先に完了した側の成果を使う
- golden は `test/selfhost/go/` に配置し、統一スクリプト（`regenerate_selfhost_golden.py`）で管理する
- golden は git 管理しない（`.gitignore` 対象）

## 決定ログ

- 2026-03-29: P6-GO-SELFHOST を起票。P1-GO-CONTAINER-WRAPPER 完了後に着手。
- 2026-03-30: S1（go build 通過）、S2（build 失敗修正）完了。全22ファイルで go build 成功。
