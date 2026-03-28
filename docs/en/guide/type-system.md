<a href="../../ja/guide/type-system.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# Type System

Pytra assumes static typing. This page explains how types are resolved, determined, and converted.

## Type Normalization

Python type names are converted to canonical types during the resolve stage.

| Python Notation | Pytra Canonical Type |
|---|---|
| `int` | `int64` |
| `float` | `float64` |
| `bool` | `bool` |
| `str` | `str` |
| `bytes` / `bytearray` | `list[uint8]` |
| `Optional[X]` | `X \| None` |

Integer types can be explicitly specified according to use case:

```python
pixel: uint8 = 255      # 0 to 255
counter: int32 = 0      # -2^31 to 2^31-1
big: int64 = 0          # -2^63 to 2^63-1 (default)
```

## type_id and isinstance

Each Pytra class has a `type_id`. `isinstance` is performed via **range checking** on these type_ids.

### How Range Checking Works

The linker assigns type_ids to all classes via DFS. A parent class's type_id range includes all of its descendants.

```
Animal  (id=1000, min=1000, max=1002)
+-- Dog (id=1001, min=1001, max=1001)
+-- Cat (id=1002, min=1002, max=1002)
```

`isinstance(dog, Animal)` is `1000 <= 1001 <= 1002` -> `True`
`isinstance(cat, Dog)` is `1001 <= 1002 <= 1001` -> `False`

This can be determined in a single comparison (O(1)).

### type_id Table

The linker generates a virtual module called `pytra.built_in.type_id_table`:

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

isinstance is implemented as:

```python
def pytra_isinstance(actual_type_id: int, tid: int) -> bool:
    return id_table[tid * 2] <= actual_type_id <= id_table[tid * 2 + 1]
```

This function and constants are defined in pure Python and automatically converted to all languages through the pipeline. No handwritten runtime is needed.

## isinstance for POD Types

Integer and floating-point types (POD types) are checked by **exact match**. Value range inclusion is not considered.

```python
x: int16 = 1
isinstance(x, int16)   # True  -- same type
isinstance(x, int8)    # False -- different type
isinstance(x, int32)   # False -- different type even though the value range is included
```

POD types have no inheritance relationships and no type_ids.

## isinstance Narrowing

Inside an `if isinstance(x, T):` block, the type of `x` is automatically narrowed to `T`.

```python
val: JsonVal = json.loads(data)

if isinstance(val, dict):
    # val is automatically treated as dict[str, JsonVal]
    val.get("key")  # OK: can be used without cast
```

Patterns where narrowing applies:
- `if isinstance(x, T):` -- inside the if block
- `elif isinstance(x, U):` -- inside the elif block
- `if not isinstance(x, T): return` -- in subsequent lines
- `y = x if isinstance(x, T) else None` -- the true side of the ternary operator

Narrowing only updates the type environment during the resolve stage; it adds no additional responsibility to the emitter.

## Union Types and Tagged Unions

Union types are declared with `type X = A | B | C`.

```python
type JsonVal = None | bool | int | float | str | list[JsonVal] | dict[str, JsonVal]
```

Internally, these are treated as tagged unions and converted to the native representation of each target language.

Branching with isinstance + narrowing automatically narrows the type:

```python
if isinstance(val, dict):
    val.get("key")      # val can be used as dict
elif isinstance(val, list):
    for item in val:     # val can be used as list
        print(item)
```

## Ternary Operator Type Inference

```python
x = expr if cond else None   # -> Optional[T]
x = a if cond else b         # -> A | B (when types differ)
x = "yes" if flag else "no"  # -> str (when types are the same)
```

resolve examines the types of the true and false sides and automatically infers the correct type.

## Automatic Numeric Type Casting

When different numeric types are mixed in an operation, resolve automatically inserts casts.

```python
x: int64 = 10
y: float64 = 3.14
z = x + y   # an int64 -> float64 cast is automatically inserted for x
```

The promotion rules follow C++ integer promotion / usual arithmetic conversion.

## Detailed Specifications

- [type_id Specification](../spec/spec-type_id.md)
- [Tagged Union Specification](../spec/spec-tagged-union.md)
- [EAST Specification S7.1](../spec/spec-east.md) -- isinstance narrowing
- [Boxing/Unboxing Specification](../spec/spec-boxing.md)
