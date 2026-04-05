<a href="../../en/plans/p3-cs-selfhost.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P3-CS-SELFHOST: C# emitter で toolchain2 を C# に変換し build を通す

最終更新: 2026-03-30
ステータス: 未着手

## 背景

P1-CS-EMITTER で C# emitter を実装した後、Pytra の変換器自身（toolchain2）を C# に変換し、変換後のコンパイラが正しく動作することを検証する。

## フロー

1. `pytra-cli -build --target cs` で toolchain2 全 `.py` を C# に変換
2. `mcs` または `dotnet build` でコンパイルしてバイナリを生成
3. バイナリで fixture/sample/stdlib を変換し、Python と同じ出力が得られるか検証（P3-SELFHOST-PARITY）

## 設計判断

- EAST の workaround 禁止。build 失敗は emitter/runtime の修正で解消する
- 型注釈補完（S0）は他言語の selfhost と共有。先に完了した側の成果を使う
- golden は `test/selfhost/cs/` に配置し、統一スクリプト（`regenerate_selfhost_golden.py`）で管理する

## 決定ログ

- 2026-03-30: C# selfhost タスクを起票。P1-CS-EMITTER 完了後に着手。
