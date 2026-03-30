<a href="../../en/plans/p3-java-selfhost.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P3-JAVA-SELFHOST: Java emitter で toolchain2 を Java に変換し build を通す

最終更新: 2026-03-30
ステータス: 未着手

## 背景

P1-JAVA-EMITTER で Java emitter を実装した後、Pytra の変換器自身（toolchain2）を Java に変換し、変換後のコンパイラが正しく動作することを検証する。

## フロー

1. `pytra-cli2 -build --target java` で toolchain2 全 `.py` を Java に変換
2. `javac` でコンパイルして class ファイルを生成
3. `java` で実行して fixture/sample/stdlib を変換し、Python と同じ出力が得られるか検証（P3-SELFHOST-PARITY）

## Java 固有の考慮事項

- Java はトップレベル関数がないため、selfhost コードは class に包む必要がある
- ジェネリクスのプリミティブ型制約（`List<long>` 不可 → `List<Long>`）が selfhost コードに影響する可能性
- checked exception の `throws` 宣言が selfhost コードの全メソッドに波及する可能性

## 設計判断

- EAST の workaround 禁止。build 失敗は emitter/runtime の修正で解消する
- 型注釈補完（S0）は他言語の selfhost と共有。先に完了した側の成果を使う
- golden は `test/selfhost/java/` に配置し、統一スクリプト（`regenerate_selfhost_golden.py`）で管理する

## 決定ログ

- 2026-03-30: Java selfhost タスクを起票。P1-JAVA-EMITTER 完了後に着手。Java が通れば Kotlin selfhost への展開が近くなる。
