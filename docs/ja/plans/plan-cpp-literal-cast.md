# 計画: C++ 整数リテラルの冗長キャスト除去 (P0-CPP-LITERAL-CAST)

## 背景

C++ emitter の `_emit_constant`（`emitter.py:1026-1027`）が、整数リテラルを常に型キャスト付きで出力している:

```cpp
// 現状: 冗長
for (int64 i = int64(0); i < max_iter; i += 1) {
int64 x = int64(42);
int32 count = int32(0);

// 理想: 安全な場合はキャストなし
for (int64 i = 0; i < max_iter; i += 1) {
int64 x = 42;
int32 count = 0;
```

## C++ の整数リテラル型規則

C++ の整数リテラル（サフィックスなし、10進数）の型は値に応じて決まる:

1. `int` に収まれば `int`（通常 32bit: -2^31 〜 2^31-1）
2. `int` に収まらなければ `long`
3. `long` に収まらなければ `long long`

代入先の型への暗黙変換は以下の場合に安全:

- **拡大変換 (widening)**: `int` → `int64_t` (= `long long`) — 常に安全
- **同幅変換**: `int` → `int32_t` (= `int`) — 常に安全

以下の場合はキャストが必要:

- **縮小変換 (narrowing)**: `int` → `int8_t`, `int16_t` — 値が範囲外だと未定義ではないが意図しない切り詰めが起きる
- **符号変換**: `int` → `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t` — 負のリテラルで問題。`-1` → `uint32_t` は `4294967295` になる
- **大きなリテラル**: `int` 範囲を超える値 — リテラル自体が `long` や `long long` になるが、明示キャストの方が意図が明確

## 判定ルール

`_emit_constant` で整数リテラル `v` と `resolved_type` `T` に対して:

| 条件 | キャスト | 理由 |
|---|---|---|
| `T` が `int64` かつ `v` が `int` 範囲内 | 不要 | `int` → `int64_t` は安全な拡大変換 |
| `T` が `int32` かつ `v` が `int` 範囲内 | 不要 | `int` → `int32_t` は同幅変換 |
| `T` が `int8` / `int16` | 必要 | narrowing conversion |
| `T` が `uint8` / `uint16` / `uint32` / `uint64` | 必要 | 符号変換のリスク |
| `v` が `int` 範囲外（|v| >= 2^31） | 必要 | リテラル型が `long` になり意図が不明確 |

`int` 範囲 = -2147483648 〜 2147483647

## 実装方針

`_emit_constant` の該当箇所（1026-1027行目）を変更:

```python
# 現状
if rt in ("int", "int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"):
    return cpp_signature_type(rt) + "(" + str(val) + ")"

# 変更後
_INT_RANGE_MIN = -(2**31)
_INT_RANGE_MAX = 2**31 - 1
if rt in ("int32", "int64") and _INT_RANGE_MIN <= val <= _INT_RANGE_MAX:
    return str(val)
if rt in ("int", "int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"):
    return cpp_signature_type(rt) + "(" + str(val) + ")"
```

## 影響範囲

- 生成コードの見た目が変わる（`int64(0)` → `0`）ため、golden の差分が出る
- **実行結果は変わらない** — C++ の暗黙変換規則に従った等価な変換
- fixture + sample の parity check で回帰がないことを確認する

## 対象外

- `float64` リテラル（`3.14` 等）のキャストは本タスクのスコープ外
- `ForRange` 等で直接ハードコードされている `int64(0)` / `int64(1)`（2445行目等）も同様に修正すべきだが、別タスクでもよい
