<a href="../../en/todo/rust.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — Rust backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-29

## 現状

- toolchain2 に Rust emitter は未実装（`src/toolchain2/emit/rs/` が存在しない）
- runtime は `src/runtime/rs/` に存在する（旧 toolchain1 時代の実装）
- 旧 toolchain1 の Rust emitter は `src/toolchain/emit/rs/` に存在するが、toolchain2 への移行が必要

## 未完了タスク

### P7-RS-EMITTER: Rust emitter を toolchain2 に新規実装する

前提: Go emitter（参照実装）と CommonRenderer が安定してから着手。

1. [ ] [ID: P7-RS-EMITTER-S1] `src/toolchain2/emit/rs/` に Rust emitter を新規実装する — Go emitter を参考に CommonRenderer + override 構成で作成。Rust 固有のノード（所有権・ライフタイム・borrow、match、impl ブロック等）だけ override として残す
2. [ ] [ID: P7-RS-EMITTER-S2] `src/runtime/rs/mapping.json` を作成し、runtime_call の写像を定義する
3. [ ] [ID: P7-RS-EMITTER-S3] fixture 132 件 + sample 18 件の Rust emit 成功を確認する
4. [ ] [ID: P7-RS-EMITTER-S4] Rust runtime を toolchain2 の emit 出力と整合させる（旧 toolchain1 runtime の引き継ぎ or 再実装）
5. [ ] [ID: P7-RS-EMITTER-S5] fixture + sample の Rust compile + run parity を通す
