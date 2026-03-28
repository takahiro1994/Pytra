<a href="../../en/guide/type-system.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 型システム

Pytra は静的型付けが前提です。このページでは、型がどのように解決・判定・変換されるかを解説します。

## 型の正規化

Python の型名は resolve 段で正規型に変換されます。

| Python 表記 | Pytra 正規型 |
|---|---|
| `int` | `int64` |
| `float` | `float64` |
| `bool` | `bool` |
| `str` | `str` |
| `bytes` / `bytearray` | `list[uint8]` |
| `Optional[X]` | `X \| None` |

整数型は用途に応じて明示できます:

```python
pixel: uint8 = 255      # 0 〜 255
counter: int32 = 0      # -2^31 〜 2^31-1
big: int64 = 0          # -2^63 〜 2^63-1（既定）
```

## type_id と isinstance

Pytra のクラスはそれぞれ `type_id` を持ちます。`isinstance` はこの type_id の **区間判定** で行われます。

### 区間判定の仕組み

linker が DFS で全クラスに type_id を割り当てます。親クラスの type_id 区間は、全ての子孫を含みます。

```
Animal  (id=1000, min=1000, max=1002)
├── Dog (id=1001, min=1001, max=1001)
└── Cat (id=1002, min=1002, max=1002)
```

`isinstance(dog, Animal)` は `1000 <= 1001 <= 1002` → `True`
`isinstance(cat, Dog)` は `1001 <= 1002 <= 1001` → `False`

1回の比較（O(1)）で判定できます。

### type_id テーブル

linker は `pytra.built_in.type_id_table` という仮想モジュールを生成します:

```python
id_table: list[int] = [
    1000, 1002,  # index 0: Animal
    1001, 1001,  # index 2: Dog
    1002, 1002,  # index 4: Cat
]

ANIMAL_TID: int = 0
DOG_TID: int = 1
CAT_TID: int = 2
```

isinstance は:

```python
def pytra_isinstance(actual_type_id: int, tid: int) -> bool:
    return id_table[tid * 2] <= actual_type_id <= id_table[tid * 2 + 1]
```

この関数と定数は pure Python で定義され、パイプラインで全言語に自動変換されます。手書き runtime は不要です。

## POD 型の isinstance

整数型や浮動小数型（POD 型）は **exact match** で判定されます。値域の包含関係は考慮しません。

```python
x: int16 = 1
isinstance(x, int16)   # True  — 同じ型
isinstance(x, int8)    # False — 別の型
isinstance(x, int32)   # False — 値域が含まれていても別の型
```

POD 型は継承関係を持たず、type_id も持ちません。

## isinstance ナローイング

`if isinstance(x, T):` の if ブロック内で、`x` の型が自動的に `T` に絞り込まれます。

```python
val: JsonVal = json.loads(data)

if isinstance(val, dict):
    # val は自動的に dict[str, JsonVal] として扱われる
    val.get("key")  # OK: cast なしで使える
```

ナローイングが効くパターン:
- `if isinstance(x, T):` — if ブロック内
- `elif isinstance(x, U):` — elif ブロック内
- `if not isinstance(x, T): return` — 以降の行で
- `y = x if isinstance(x, T) else None` — 三項演算子の真側

ナローイングは resolve 段で型環境を更新するだけであり、emitter に追加の責務はありません。

## union 型と tagged union

`type X = A | B | C` で union 型を宣言します。

```python
type JsonVal = None | bool | int | float | str | list[JsonVal] | dict[str, JsonVal]
```

内部的には tagged union として扱われ、各ターゲット言語のネイティブな表現に変換されます。

isinstance + ナローイングで分岐すると、自動的に型が絞り込まれます:

```python
if isinstance(val, dict):
    val.get("key")      # val は dict として扱える
elif isinstance(val, list):
    for item in val:     # val は list として扱える
        print(item)
```

## 三項演算子の型推論

```python
x = expr if cond else None   # → Optional[T]
x = a if cond else b         # → A | B（型が異なる場合）
x = "yes" if flag else "no"  # → str（型が同じ場合）
```

resolve が真側と偽側の型を見て、自動的に正しい型を推論します。

## 数値型の自動 cast

異なる数値型が混在する演算では、resolve が自動的に cast を挿入します。

```python
x: int64 = 10
y: float64 = 3.14
z = x + y   # x に int64 → float64 の cast が自動挿入される
```

C++ の integer promotion / usual arithmetic conversion に準拠した昇格ルールです。

## 詳しい仕様

- [type_id 仕様](../spec/spec-type_id.md)
- [tagged union 仕様](../spec/spec-tagged-union.md)
- [EAST 仕様 §7.1](../spec/spec-east.md) — isinstance ナローイング
- [Boxing/Unboxing 仕様](../spec/spec-boxing.md)
