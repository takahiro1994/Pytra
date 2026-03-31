# 計画: EAST の tuple unpack バグ修正 (P0-EAST-TUPLE-UNPACK)

## 背景

`tuple_unpack_variants` fixture で EAST3 の tuple unpack に 3 パターンのバグが発見された。Python では合法な構文だが、EAST3 で正しく表現されない。

## バグ一覧

| パターン | EAST3 の結果 | 状態 |
|---|---|---|
| `x, y, z = 1, 2, 3` | `TupleUnpack` | ✅ 正常 |
| `(x, y, z) = (1, 2, 3)` | `Expr` に崩壊（代入が消える） | ❌ バグ |
| `[x, y, z] = [1, 2, 3]` | `Expr` に崩壊（代入が消える） | ❌ バグ |
| `x, y, z = [1, 2, 3]` | `TupleUnpack` | ✅ 正常 |
| `x, y, z = [i for i in range(3)]` | comprehension 展開で unpack 代入が消失 | ❌ バグ |
| `a[0], a[1], a[2] = [1, 2, 3]` | `TupleUnpack` | ✅ 正常 |
| `a, (b, c) = 1, (2, 3)` | `TupleUnpack` | ✅ 正常 |
| `x, y = y, x` | `Swap` | ✅ 正常 |

## 原因分析

### バグ 1: 括弧付き左辺 `()` / `[]`

`(x, y, z) = ...` と `[x, y, z] = ...` で左辺が括弧/角括弧で囲まれている場合、parser が代入ターゲットとして認識できず `Expr` に崩している。

Python の AST では `(x, y, z)` も `[x, y, z]` も `x, y, z` と同じ代入ターゲットとして扱われる。EAST の parser がこの等価性を処理していない。

### バグ 2: comprehension + unpack

`x, y, z = [i for i in range(3)]` で:
1. list comprehension が `__comp_1` に展開される（正しい）
2. しかし `x, y, z = __comp_1` の tuple unpack 代入が生成されない（バグ）

comprehension の展開パスが元の代入ターゲットの情報を失っている。

## 修正方針

### バグ 1

EAST1 parser（`src/toolchain2/parse/py/` または `src/toolchain/misc/east_parts/core.py`）で、代入文の左辺が `()` または `[]` で囲まれた Tuple/List の場合も、括弧なしの tuple target と同様に `TupleUnpack` に変換する。

### バグ 2

EAST2 または EAST3 の list comprehension 展開パスで、元の代入ターゲットが Tuple の場合に、展開後の `__comp_N` から各変数へのインデックスアクセス代入を生成する:

```
__comp_1 = [i for i in range(3)]  # comprehension 展開
x = __comp_1[0]                    # tuple unpack 展開
y = __comp_1[1]
z = __comp_1[2]
```

## fixture

`test/fixture/source/py/typing/tuple_unpack_variants.py` に全 8 パターンを含むテストを配置済み。Python では全て PASS。
