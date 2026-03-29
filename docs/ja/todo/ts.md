<a href="../../en/todo/ts.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — TypeScript / JavaScript backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-29

## 現状

- toolchain2 に TS/JS emitter は未実装（`src/toolchain2/emit/ts/`, `src/toolchain2/emit/js/` が存在しない）
- runtime は `src/runtime/ts/`, `src/runtime/js/` に存在する（旧 toolchain1 時代の実装）
- 旧 toolchain1 の TS/JS emitter は `src/toolchain/emit/ts/`, `src/toolchain/emit/js/` に存在するが、toolchain2 への移行が必要
- TS emitter は JS emitter に型注釈を追加する薄いラッパーとして設計される想定

## 未完了タスク

### P8-TS-EMITTER: TypeScript emitter を toolchain2 に新規実装する

前提: Go emitter（参照実装）と CommonRenderer が安定してから着手。

1. [ ] [ID: P8-TS-EMITTER-S1] `src/toolchain2/emit/js/` に JavaScript emitter を新規実装する — CommonRenderer + override 構成。JS 固有のノード（prototype chain、arrow function、destructuring 等）だけ override として残す
2. [ ] [ID: P8-TS-EMITTER-S2] `src/toolchain2/emit/ts/` に TypeScript emitter を新規実装する — JS emitter を継承し、型注釈を追加する薄いレイヤー
3. [ ] [ID: P8-TS-EMITTER-S3] `src/runtime/js/mapping.json`, `src/runtime/ts/mapping.json` を作成し、runtime_call の写像を定義する
4. [ ] [ID: P8-TS-EMITTER-S4] fixture 132 件 + sample 18 件の JS/TS emit 成功を確認する
5. [ ] [ID: P8-TS-EMITTER-S5] JS/TS runtime を toolchain2 の emit 出力と整合させる
6. [ ] [ID: P8-TS-EMITTER-S6] fixture + sample の JS/TS run parity を通す（node 実行）
