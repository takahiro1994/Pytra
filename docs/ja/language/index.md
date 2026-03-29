<a href="../../en/language/index.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 言語別仕様

各ターゲット言語の個別仕様をまとめた入口です。

- [プロジェクト進捗](./progress.md) — バックエンドサポート状況、タスク一覧、更新履歴
- 旧マトリクス: [archive/](./archive/) に退役済み
- C++:
  - サポート状況（テスト根拠つき）: [py2cpp サポートマトリクス](./cpp/spec-support.md)
- Julia:
  - native emitter（EAST3 直接生成）: `src/toolchain/emit/julia/`
  - ランタイム: `src/runtime/julia/built_in/py_runtime.jl`
- Dart:
  - native emitter（EAST3 直接生成）: `src/toolchain/emit/dart/`
  - ランタイム: `src/runtime/dart/built_in/py_runtime.dart`
- Zig:
  - native emitter（EAST3 直接生成）: `src/toolchain/emit/zig/`
  - ランタイム: `src/runtime/zig/built_in/py_runtime.zig`
