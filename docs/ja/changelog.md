# 更新履歴

## 2026-03-26

- **パイプライン再設計完了**: parse → resolve → compile → optimize → link → emit の 6 段パイプライン（`pytra-cli2`）が全段動作。toolchain2 は toolchain に一切依存しない独立実装。
- **Go backend 新パイプライン移行**: Go emitter + runtime を新パイプラインで実装。sample 18/18 emit 成功。旧 Go emitter/runtime を削除。
- **C++ emitter 新規実装**: `toolchain2/emit/cpp/` に新パイプライン用 C++ emitter を実装。fixture 132/132, sample 18/18 emit 成功。
- **CodeEmitter 基底クラス**: `mapping.json` による runtime_call 写像を全 emitter で共有。ハードコード除去。
- **仕様整合 (Codex-review)**: resolve/parser/validator/linker/emitter の仕様違反 20 件以上を修正。
- **spec-east1.md / spec-east2.md**: EAST1（型未解決）と EAST2（型確定）の出力契約を正式定義。
- **spec-builtin-functions.md**: built-in 関数の宣言仕様。POD/Obj 型分類、dunder 委譲、extern_fn/extern_var/extern_class/extern_method。
- **spec-runtime-mapping.md**: mapping.json のフォーマット仕様。implicit_promotions テーブル。
- **integer promotion**: C++ usual arithmetic conversion に準拠した数値昇格 cast を resolve で挿入。
- **bytearray 対応**: `pytra/utils/png.py` / `gif.py` を `list[int]` → `bytearray` に書き換え。Go で `[]byte` に写像。

## 2026-03-25

- **P0 全完了**: parse/resolve/compile/optimize/link/emit の全段が golden file テストと一致。
- **test/ ディレクトリ再編**: fixture/sample/include/pytra/selfhost の 5 カテゴリに整理。
- **golden file 自動再生成**: `tools/regenerate_golden.py` で全段 golden を一括再生成。
- **Go emitter**: お手本 emitter として実装。fixture 132/132, sample 18/18 emit 成功。
- **Go runtime + parity**: sample 18/18 で `go run` + stdout 一致。Go は Python の 63x 高速。
- **Go runtime 分解**: `pytra_runtime.go` 全部入り → `built_in/` + `std/` + `utils/` に分離。

## 2026-03-24

- **パイプライン再設計着手**: parse/resolve/compile/optimize/emit の 5 段（後に link 追加で 6 段）パイプラインを設計。
- **toolchain2/ 新規作成**: 現行 toolchain/ とは独立した新パイプライン実装。selfhost 対象（Any/object 禁止、pytra.std のみ）。
- **pytra-cli2**: 新 CLI。-parse/-resolve/-compile/-optimize/-link/-emit/-build サブコマンド。
- **EAST1 golden file**: spec-east1 準拠で golden を strip（型情報除去）。150 件。
- **built-in 関数宣言**: `src/include/py/pytra/built_in/builtins.py` + `containers.py`。v2 extern（extern_fn/extern_var/extern_class/extern_method）。
- **stdlib 宣言**: `src/include/py/pytra/std/` に math/time/glob/os/sys 等の v2 extern 宣言。

## 2026-03-23 以前

- v0.15.0 リリース。backend として PowerShell をサポート。
- v0.14.0 リリース。再帰的 union type をサポート。
- v0.13.0 リリース。NES エミュレーターを Python + SDL3 で作成。
- 過去ニュース: [docs/ja/news/index.md](news/index.md)
