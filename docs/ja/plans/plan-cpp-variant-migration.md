# 計画: C++ を std::variant ベースに移行し object/box/unbox を廃止する

## 背景

現在の C++ runtime は union type を `object`（`{type_id, rc<RcObject>}`）に退化させ、boxing/unboxing で値を出し入れしている。これが emitter の複雑さの根本原因。

`work/tmp/variant_test.cpp` で以下を実証済み:
- `std::variant<int64_t, std::string, NoneType>` で基本 union が動く
- 再帰型は `struct { variant<..., shared_ptr<vector<Self>>> }` で前方参照 + RC 共有が動く
- isinstance は `std::holds_alternative<T>()` で言語ネイティブ
- callable は `std::function` で動く

## 段階的移行

### Phase 1: C++ emitter に variant 出力を追加

EAST3 の `UnionType` を見て `std::variant<T1, T2, ...>` を生成する。

1. C++ emitter の型変換に `UnionType` → `std::variant<...>` パスを追加
2. `OptionalType` → `std::optional<T>` パスを追加（既存かもしれない）
3. isinstance narrowing を `std::holds_alternative<T>` + `std::get<T>` に変換
4. 再帰型は `struct { variant<..., shared_ptr<vector<Self>>> }` で出力
5. この時点では `object` パスも残す（fallback）

完了条件: `int | str`, `str | None`, `int | float | None` 等の基本 union を使う fixture が C++ で PASS

### Phase 2: C++ から object 型を削除

Phase 1 で variant が動いたら、`object` への退化パスを削除する。

1. C++ emitter の `object` 型出力を全て `std::variant` に置換
2. `Box` ノードの C++ 出力を variant への直接代入に変更
3. `Unbox` ノードの C++ 出力を `std::get<T>` に変更
4. `type_id` ベースの isinstance を `std::holds_alternative<T>` に置換
5. `PYTRA_TID_*` 定数、`g_type_table`（既に撤去済み）、`py_runtime_object_type_id` 等を削除
6. `object.h` の `object` クラスを削除または縮退

完了条件: C++ fixture 全件 + sample 全件が `object` 型なしで PASS

### Phase 3: C++ から box/unbox 処理を削除

1. C++ emitter の `_emit_box` / `_emit_unbox` を削除
2. variant への代入は通常の代入として emit
3. variant からの取り出しは `std::holds_alternative` + `std::get` として emit
4. `yields_dynamic` フラグに依存する emitter コードを削除

完了条件: C++ emitter に box/unbox 関連コードがゼロ

### Phase 4: EAST から object 退化 / box / unbox を削除

Phase 2-3 で C++ が動いたら、EAST3 の lowering を変更する。

1. lower.py:597 の Boxing（`resolved_type="object"` 生成）を削除
2. lower.py:2042-2075 の iter boundary（`resolved_type="object"` 生成）を削除
3. `Box` / `Unbox` ノード種別を `VariantStore` / `VariantNarrow` に改名（or 廃止）
4. `yields_dynamic` フラグを廃止
5. EAST3 validation に「`resolved_type: "object"` が含まれていたらエラー」を追加
6. type_summary.py / type_norm.py の `"object"` 正規化を削除

完了条件: EAST3 出力に `object` / `Box` / `Unbox` が出現しない。全言語の fixture + sample が PASS

### Phase 5: 他言語への展開

EAST から object/box/unbox が消えた後、他言語の emitter を更新:

- Rust: `enum` に変換（既に PyAny enum を持っている、variant ベースに統一）
- Go: `any` のまま（type switch で使う、変更不要）
- TS: union そのまま（変更不要）
- C#: sealed record / abstract class
- Java: sealed class
- 動的型言語: 変更不要

## 注意事項

### int リテラルの ambiguity

`std::variant<int64_t, double, bool>` に `int` リテラルを入れると ambiguity が出る（実証済み）。emitter は `int64_t(42)` のように型を明示する必要がある。P0-CPP-LITERAL-CAST の `literal_nowrap_ranges` と連携が必要。

### Optional との関係

`T | None` は `std::optional<T>` で表現できるが、`std::variant<T, NoneType>` でも動く。EAST3 の `OptionalType` と `UnionType` の使い分けを明確にする必要がある。

### selfhost への影響

selfhost コードは `JsonVal` を多用しているが、`JsonVal` は nominal ADT（spec-east.md §6.5）。`object` に退化させずに `struct { variant<...> }` として変換すれば、selfhost の崩壊パターンも解消される見込み。ただし Phase 1-3 が安定してから selfhost を再試行すること。

## 関連

- [spec-adt.md](../spec/spec-adt.md): ADT 仕様（object 退化禁止）
- [plan-union-to-nominal-adt.md](./plan-union-to-nominal-adt.md): 全言語の移行計画
- `work/tmp/variant_test.cpp`: 実証コード
