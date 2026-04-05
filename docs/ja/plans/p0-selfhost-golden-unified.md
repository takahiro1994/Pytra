<a href="../../en/plans/p0-selfhost-golden-unified.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P0-SELFHOST-GOLDEN-UNIFIED: selfhost golden の生成・検証スクリプトを1本に統一する

最終更新: 2026-03-30
ステータス: 未着手

## 背景

各 backend 担当が独自に selfhost golden スクリプトを作っている（例: C++ 担当の `test_cpp_selfhost_golden.py`）。このままでは言語が増えるたびに似たスクリプトが乱立し、メンテナンスコストが増大する。

golden の生成と検証を1本のスクリプトに統一し、全言語で同じ仕組みを使う。

## 設計

### 生成スクリプト

`tools/gen/regenerate_selfhost_golden.py`

```bash
# 全言語の selfhost golden を一括生成
python3 tools/gen/regenerate_selfhost_golden.py

# 特定言語のみ
python3 tools/gen/regenerate_selfhost_golden.py --target cpp,go
```

処理:
1. toolchain2 全 `.py` を指定言語に emit（`pytra-cli -build --target <lang>`）
2. emit 結果を `test/selfhost/<lang>/` に配置
3. 既存の golden がある場合は diff を報告

### 回帰テスト

`tools/unittest/selfhost/test_selfhost_golden.py`

全言語共通で:
1. golden ファイルが最新の emit 結果と一致するか検証
2. ターゲット言語のコンパイラが通るか検証（`g++`, `go build`, `rustc`, `tsc` 等）

言語ごとのパラメータ（コンパイルコマンド、ファイル拡張子等）はテーブルで定義し、言語別スクリプトを不要にする。

### 配置先

```
test/selfhost/
  cpp/         ← C++ selfhost golden
  go/          ← Go selfhost golden
  rs/          ← Rust selfhost golden
  ts/          ← TS selfhost golden
```

### 廃止対象

言語別の個別スクリプト（`test_cpp_selfhost_golden.py` 等）は `tools/unregistered/` に退避する。

## 決定ログ

- 2026-03-30: C++ 担当が `test_cpp_selfhost_golden.py` を独自に作成。言語別スクリプトの乱立を防ぐため、統一スクリプトの必要性を確認。
