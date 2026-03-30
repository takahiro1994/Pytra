<a href="../../en/plans/p1-nim-emitter.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P1-NIM-EMITTER: Nim emitter を toolchain2 に新規実装する

最終更新: 2026-03-31
ステータス: S1-S4 完了、S5-S6 は Nim コンパイラ要

## 背景

旧 toolchain1 に Nim emitter と runtime が存在するが、toolchain2 の新パイプラインに移行する必要がある。

## 設計

- `src/toolchain2/emit/nim/` に CommonRenderer + override 構成で実装
- 旧 `src/toolchain/emit/nim/` と TS emitter（`src/toolchain2/emit/ts/`）を参考にする
- `src/runtime/nim/mapping.json` に `calls`, `types`, `env.target`, `builtin_prefix`, `implicit_promotions` を定義
- parity check: `runtime_parity_check_fast.py --targets nim` で fixture + sample + stdlib の3段階検証

## 決定ログ

- 2026-03-31: Nim backend 担当を新設。emitter guide に従い toolchain2 emitter を実装する方針。
- 2026-03-31: S1-S4 完了。emitter.py (1962行), types.py, profiles/nim.json, mapping.json を作成。fixture 129/131 emit 成功（残り2件は parser 側 trait 未対応）。py_runtime.nim を大幅拡充（py_print, str methods, container helpers, assert framework 等）。
