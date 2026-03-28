<a href="../../ja/guide/extern-ffi.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# @extern and FFI

This page explains the mechanism for calling native functions and libraries in each target language from Pytra code.

## What is @extern?

`@extern` is a decorator that declares "this function is implemented on the target language side." On the Pytra side, you only write the signature (argument and return types) without a body.

```python
@extern
def native_sqrt(x: float) -> float: ...

if __name__ == "__main__":
    print(native_sqrt(2.0))
```

The emitter sees this declaration and generates code that calls `native_sqrt` on the target language side.

## Usage Example: SDL3 Bindings

When you want to use an external library:

```python
@extern
def sdl_init(flags: int) -> int: ...

@extern
def sdl_create_window(title: str, w: int, h: int, flags: int) -> int: ...

@extern
def sdl_destroy_window(window: int) -> None: ...

if __name__ == "__main__":
    sdl_init(0)
    win = sdl_create_window("Hello", 800, 600, 0)
    # ... use it ...
    sdl_destroy_window(win)
```

On the target language side, you provide implementations that bind `sdl_init`, `sdl_create_window`, and `sdl_destroy_window` to the C SDL3 API.

## @abi -- Type Control at ABI Boundaries

`@abi` controls how function arguments are passed.

```python
from pytra.std import abi

@abi(args={"data": "value_mut"})
def process(data: list[int]) -> None:
    data.append(42)
```

| Mode | Meaning |
|---|---|
| `default` | Language default method |
| `value` | Pass by value (read-only) |
| `value_mut` | Pass by value (mutable) |

Usually `default` is sufficient, but explicit control may be needed when interacting with C libraries via FFI.

## @template -- Generic Functions

`@template` defines a function with type parameters.

```python
from pytra.std import template

@template("T")
def identity(x: T) -> T:
    return x

if __name__ == "__main__":
    print(identity(42))        # T = int
    print(identity("hello"))   # T = str
```

This is converted to templates in C++, generics in Rust, and type parameters in Go.

## extern Classes

You can also make an entire class extern:

```python
@extern
class NativeWindow:
    width: int
    height: int

    def resize(self, w: int, h: int) -> None: ...
    def close(self) -> None: ...
```

On the target language side, you provide the implementation of the `NativeWindow` class. The Pytra side only knows the interface (signatures).

## How extern Works

1. The parser preserves `@extern` in EAST1
2. resolve registers the extern function's signature in the type environment (types are determined even without a body)
3. In EAST3, it is preserved as `decorators: ["extern"]`
4. The emitter generates **delegation code** (a thin wrapper to the native function) based on the signature
5. The user provides the implementation on the target language side

The emitter only generates delegation code based on the signature; it does not generate the implementation body.

## extern in the Runtime

Some functions in `pytra/std/*` modules (math, time, pathlib, etc.) are internally implemented using `@extern`. For example, `perf_counter()`:

1. Declared as `@extern def perf_counter() -> float: ...` in `pytra/std/time.py`
2. Each language's runtime has a native implementation of `perf_counter`
3. The emitter maps the name according to `mapping.json`

When a user writes `from pytra.std.time import perf_counter`, this mechanism works behind the scenes.

## Detailed Specifications

- [User Specification](../spec/spec-user.md) -- @extern input constraints
- [Emitter Guidelines S4](../spec/spec-emitter-guide.md) -- @extern delegation code generation
