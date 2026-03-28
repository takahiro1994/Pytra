<a href="../../ja/guide/emitter-overview.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# How the Emitter Works

The emitter takes EAST3 (the instruction-level intermediate representation) and outputs source code in the target language. This page compares how the same EAST3 is transformed for each language side by side.

## Emitter Principles

What the emitter does is **simply map EAST3 nodes to target language syntax**.

- It does not perform type inference (already resolved in EAST3)
- It does not add casts (already inserted in EAST3)
- It does not resolve runtime call names (already defined in mapping.json)

By keeping the emitter free of semantic decisions and focused solely on syntactic translation, adding support for new languages becomes easier.

## Before and After Comparison

### Variable Declarations

```python
x: int = 42
name: str = "hello"
items: list[int] = [1, 2, 3]
```

| Language | Output |
|---|---|
| C++ | `int64 x = 42; str name = str("hello"); Object<list<int64>> items = rc_list_new<int64>({1, 2, 3});` |
| Go | `x := int64(42); name := "hello"; items := NewPyList([]int64{1, 2, 3})` |
| Rust | `let x: i64 = 42; let name = String::from("hello"); let items = vec![1i64, 2, 3];` |
| Java | `long x = 42; String name = "hello"; ArrayList<Long> items = new ArrayList<>(List.of(1L, 2L, 3L));` |

Type name conversions are defined in the `types` map of the language profile (`profiles/<lang>.json`).

### if Statements

```python
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
else:
    print("negative")
```

| Language | Condition Parens | Block | Statement Terminator |
|---|---|---|---|
| C++ | `if (x > 0)` | `{ }` | `;` |
| Go | `if x > 0` | `{ }` | none |
| Rust | `if x > 0` | `{ }` | `;` |

These differences are absorbed by `condition_parens` and `stmt_terminator` in the language profile.

### Classes and Methods

```python
class Circle(Shape):
    radius: float

    def __init__(self, r: float) -> None:
        self.radius = r

    def area(self) -> float:
        return 3.14 * self.radius * self.radius
```

**C++:**
```cpp
class Circle : public Shape {
public:
    float64 radius;
    Circle(float64 r) : radius(r) {}
    float64 area() const { return 3.14 * this->radius * this->radius; }
};
```

**Go:**
```go
type Circle struct {
    Shape
    Radius float64
}
func NewCircle(r float64) *Circle { return &Circle{Radius: r} }
func (c *Circle) Area() float64 { return 3.14 * c.Radius * c.Radius }
```

Class structure varies significantly across languages, so each language's emitter handles it individually rather than using CommonRenderer's shared logic.

### Exception Handling

```python
try:
    x = parse_int(s)
except ValueError as e:
    x = 0
finally:
    cleanup()
```

**C++ (native_throw):**
```cpp
{
    auto _finally = pytra_scope_guard([&]() { cleanup(); });
    try {
        x = parse_int(s);
    } catch (PytraValueError& e) {
        x = 0;
    }
}
```

**Go (union_return):**
```go
func() {
    defer cleanup()
    _tmp, _err := parseInt(s)
    if _err != nil {
        if pytraErrorIsInstance(_err, VALUE_ERROR_TID) {
            x = 0
            return
        }
        panic(_err)
    }
    x = _tmp
}()
```

Languages with exceptions use native throw/catch, while Go/Rust/Zig are automatically converted to return-value-based error propagation. The user's code remains the same.

## mapping.json

Runtime function name translation is defined in `mapping.json`. Hardcoding in the emitter is prohibited.

```json
{
  "builtin_prefix": "__pytra_",
  "calls": {
    "py_print": "py_print",
    "py_len": "py_len",
    "py_int_from_str": "std::stoll",
    "list.append": "py_list_append_mut"
  }
}
```

For example, `py_int_from_str` maps to `std::stoll` in C++ and to a different function name in Go, with each language having its own mapping.

## CommonRenderer

Many EAST3 nodes (if, while, BinOp, Call, Return, etc.) have the same structure across languages. CommonRenderer is the base class that handles these common nodes, and each language's emitter only overrides language-specific nodes (ClassDef, FunctionDef, etc.).

```
CommonRenderer (shared)
  +-- emit_if()      -> absorbs differences via language profile's condition_parens / block_braces
  +-- emit_binop()   -> converts operators via operator_map
  +-- emit_call()    -> converts names via mapping.json
  +-- emit_return()  -> "return" + expression

CppEmitter(CommonRenderer)
  +-- emit_class_def()  -> C++-specific syntax

GoEmitter(CommonRenderer)
  +-- emit_func_decl()  -> Go-specific return value position
```

## Detailed Specifications

- [Emitter Implementation Guidelines](../spec/spec-emitter-guide.md)
- [Language Profile Specification](../spec/spec-language-profile.md)
- [Runtime Mapping Specification](../spec/spec-runtime-mapping.md)
