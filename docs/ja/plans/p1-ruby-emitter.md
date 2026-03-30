<a href="../../en/plans/p1-ruby-emitter.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P1-RUBY-EMITTER: Ruby emitter を toolchain2 に新規実装する

最終更新: 2026-03-31
ステータス: S1-S3 完了、S4-S6 未着手

## 背景

旧 toolchain1 に Ruby emitter と runtime が存在するが、toolchain2 の新パイプラインに移行する必要がある。

## 設計

- `src/toolchain2/emit/ruby/` に CommonRenderer + override 構成で実装
- 旧 `src/toolchain/emit/ruby/` と TS emitter（`src/toolchain2/emit/ts/`）を参考にする
- `src/runtime/ruby/mapping.json` に `calls`, `types`, `env.target`, `builtin_prefix`, `implicit_promotions` を定義
- parity check: `runtime_parity_check_fast.py --targets ruby` で fixture + sample + stdlib の3段階検証

## 決定ログ

- 2026-03-31: Ruby backend 担当を新設。emitter guide に従い toolchain2 emitter を実装する方針。
- 2026-03-31: S1-S3 完了。`src/toolchain2/emit/ruby/` に emitter を新規実装。mapping.json 作成。全1031件のlinked fixture で emit 成功（0 failures）。parity check ツールに Ruby の emit/runtime copy/run dispatch を追加。
