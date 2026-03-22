# P7: math.pi 等のモジュール定数の型推論

最終更新: 2026-03-22

関連 TODO:
- `docs/ja/todo/index.md` の `ID: P7-MODULE-CONST-TYPE`

## 背景

`2.0 * math.pi * t` のような式で `math.pi` の `resolved_type` が `unknown` になり、emitter が型不一致を起こす。

`math.pi` は `float64` 定数だが、EAST1 パーサーが `math` モジュールの `pi` 属性の型を推論できていない。`signature_registry` にモジュール属性の型情報を登録すれば解決できる。

## 設計

`math.pi` の型は `math.east`（= `src/pytra/std/math.py` から生成された EAST3）に定義されている。linker がモジュールを解決した後、linked program のモジュール間で属性の型を解決すべき。EAST1 パーサーに個別モジュールの型情報をハードコードしてはならない。

アプローチ:
1. linker が `math.east` をロードした時点で、モジュールのトップレベル定数（`pi: float = 3.14159...`）の型を export テーブルに登録
2. EAST3 の `math.pi` Attribute ノードの `resolved_type` を linker が解決済みの型で更新
3. または emitter が linked program のモジュール情報から `math.pi` の型を引く

## 対象

- `src/toolchain/link/` — linker のモジュール間型解決
- または EAST3 post-link pass

## 子タスク

- [ ] [ID: P7-MODULE-CONST-TYPE-01] linker でモジュール定数の型を解決し、Attribute ノードの `resolved_type` を更新する
- [ ] [ID: P7-MODULE-CONST-TYPE-02] ユニットテストを追加する

## 決定ログ

- 2026-03-22: Zig 担当が `2.0 * math.pi * t` で `resolved_type=unknown` になる問題を報告。全 backend 共通の改善として起票。
