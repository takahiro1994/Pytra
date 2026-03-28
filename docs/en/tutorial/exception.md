<a href="../../ja/tutorial/exception.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# Exception Handling

This page explains how to use exception handling (`raise` / `try` / `except` / `finally`) in Pytra.

## Basics: raise and try/except

You can throw and catch errors using the same syntax as Python.

```python
from pytra.built_in.error import ValueError

def parse_int(s: str) -> int:
    if not s.isdigit():
        raise ValueError("not a number: " + s)
    return int(s)

if __name__ == "__main__":
    try:
        x = parse_int("abc")
        print(x)
    except ValueError as e:
        print("error: " + e.msg)
```

Output:

```text
error: not a number: abc
```

## Available Exception Types

Pytra's built-in exceptions are defined in `pytra.built_in.error`.

```python
from pytra.built_in.error import (
    PytraError,          # Base of all exceptions
    ValueError,          # Value error
    RuntimeError,        # Runtime error
    FileNotFoundError,   # File not found
    PermissionError,     # Permission denied
    TypeError,           # Type error
    IndexError,          # Index out of range
    KeyError,            # Key not found
    OverflowError,       # Overflow
)
```

Hierarchy:

```
PytraError
├── ValueError
├── RuntimeError
├── FileNotFoundError
├── PermissionError
├── TypeError
├── IndexError
├── KeyError
└── OverflowError
```

## Defining Your Own Exceptions

You can create custom exceptions by inheriting from built-in exceptions and adding fields.

```python
from pytra.built_in.error import ValueError

class ParseError(ValueError):
    line: int

    def __init__(self, line: int, msg: str) -> None:
        super().__init__(msg)
        self.line = line

def parse(s: str, line: int) -> int:
    if not s.isdigit():
        raise ParseError(line, "not a number: " + s)
    return int(s)

if __name__ == "__main__":
    try:
        x = parse("abc", 42)
    except ParseError as e:
        print("line " + str(e.line) + ": " + e.msg)
```

Output:

```text
line 42: not a number: abc
```

## except Catches Derived Classes Too

`except ValueError` catches not only `ValueError` itself but also all its derived classes (like `ParseError`). This is the same behavior as Python.

```python
try:
    x = parse("abc", 42)    # raises ParseError
except ValueError as e:      # catches ParseError too (it derives from ValueError)
    print("caught: " + e.msg)
```

## Multiple except Handlers

```python
from pytra.built_in.error import ValueError, RuntimeError

try:
    data = read_file(path)
except FileNotFoundError as e:
    data = ""
except PermissionError as e:
    raise RuntimeError("no access: " + e.msg)
```

Handlers are checked top to bottom, and the first matching one is executed.

## finally

A `finally` block is always executed, whether the try block succeeds or raises an error.

```python
try:
    f = open(path, "wb")
    f.write(data)
except ValueError as e:
    print("error: " + e.msg)
finally:
    f.close()    # always executed
```

## Error Propagation

Errors not caught by `try/except` automatically propagate to the caller.

```python
def step1(s: str) -> int:
    return parse_int(s)        # parse_int raises → propagates up

def step2(s: str) -> str:
    x = step1(s)               # step1's raise → propagates up
    return str(x * 2)

if __name__ == "__main__":
    try:
        result = step2("abc")  # caught here
    except ValueError as e:
        print("caught: " + e.msg)
```

## Works Across All Languages

Pytra's exception handling works across all 18 target languages.

- **C++, Java, C#, etc.** (languages with exceptions): Converted to native `throw` / `try-catch`
- **Go, Rust, Zig** (languages without exceptions): Automatically converted to return-value-based error propagation

You don't need to be aware of language differences. The same `raise` / `try/except` works in every language.

## Exception Types Are Just Classes

Pytra's exception types are ordinary classes. There is no special mechanism.

- Follow single inheritance
- Can have fields
- Can be checked with `isinstance` (the internal mechanism of `except`)
- Efficiently checked via `type_id`

## Summary

| Goal | How to write |
|---|---|
| Throw an error | `raise ValueError("msg")` |
| Catch an error | `try: ... except ValueError as e: ...` |
| Guarantee cleanup | `finally: cleanup()` |
| Define your own exception | `class MyError(ValueError): ...` |
| Import exceptions | `from pytra.built_in.error import ValueError` |

For detailed specifications, see:
- [Exception handling specification](../spec/spec-exception.md) — Conversion rules for each language, EAST nodes, union_return details
