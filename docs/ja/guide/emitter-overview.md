<a href="../../en/guide/emitter-overview.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# emitter の仕組み

emitter は EAST3（命令化済みの中間表現）を受け取り、ターゲット言語のソースコードを出力します。このページでは、同じ EAST3 が各言語でどう変換されるかを並べて見ます。

## emitter の原則

emitter がやることは **EAST3 ノードをターゲット言語の構文に写像するだけ** です。

- 型の推論をしない（EAST3 で確定済み）
- cast を追加しない（EAST3 で挿入済み）
- runtime call の名前解決をしない（mapping.json で定義済み）

emitter に意味の判断をさせず、表記の変換に専念させることで、新しい言語の追加が楽になります。

## 変換前後の比較

### 変数宣言

```python
x: int = 42
name: str = "hello"
items: list[int] = [1, 2, 3]
```

| 言語 | 出力 |
|---|---|
| C++ | `int64 x = 42; str name = str("hello"); Object<list<int64>> items = rc_list_new<int64>({1, 2, 3});` |
| Go | `x := int64(42); name := "hello"; items := NewPyList([]int64{1, 2, 3})` |
| Rust | `let x: i64 = 42; let name = String::from("hello"); let items = vec![1i64, 2, 3];` |
| Java | `long x = 42; String name = "hello"; ArrayList<Long> items = new ArrayList<>(List.of(1L, 2L, 3L));` |

型名の変換は言語プロファイル（`profiles/<lang>.json`）の `types` マップで定義されます。

### if 文

```python
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
else:
    print("negative")
```

| 言語 | 条件括弧 | ブロック | 文末 |
|---|---|---|---|
| C++ | `if (x > 0)` | `{ }` | `;` |
| Go | `if x > 0` | `{ }` | なし |
| Rust | `if x > 0` | `{ }` | `;` |

この差は言語プロファイルの `condition_parens` と `stmt_terminator` で吸収されます。

### クラスとメソッド

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

クラスの構造は言語間で大きく異なるため、CommonRenderer の共通処理ではなく、各言語の emitter が個別に処理します。

### 例外処理

```python
try:
    x = parse_int(s)
except ValueError as e:
    x = 0
finally:
    cleanup()
```

**C++（native_throw）:**
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

**Go（union_return）:**
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

例外がある言語はネイティブの throw/catch を使い、Go/Rust/Zig は戻り値ベースのエラー伝播に自動変換されます。ユーザーのコードは同じです。

## mapping.json

runtime 関数の名前変換は `mapping.json` で定義します。emitter がハードコードすることは禁止されています。

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

`py_int_from_str` → C++ では `std::stoll`、Go では別の関数名、というように言語ごとに mapping を持ちます。

## CommonRenderer

多くの EAST3 ノード（if, while, BinOp, Call, Return 等）は言語間で構造が同じです。CommonRenderer はこれらの共通ノードを処理する基底クラスで、各言語の emitter は言語固有のノード（ClassDef, FunctionDef 等）だけを override します。

```
CommonRenderer（共通）
  ├── emit_if()      → 言語プロファイルの condition_parens / block_braces で差を吸収
  ├── emit_binop()   → operator_map で演算子を変換
  ├── emit_call()    → mapping.json で名前を変換
  └── emit_return()  → "return" + 式

CppEmitter(CommonRenderer)
  └── emit_class_def()  → C++ 固有の構文

GoEmitter(CommonRenderer)
  └── emit_func_decl()  → Go 固有の戻り値位置
```

## 詳しい仕様

- [Emitter 実装ガイドライン](../spec/spec-emitter-guide.md)
- [言語プロファイル仕様](../spec/spec-language-profile.md)
- [runtime mapping 仕様](../spec/spec-runtime-mapping.md)
