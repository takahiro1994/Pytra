<a href="../../ja/guide/east-overview.md">
  <img alt="Read in Japanese" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# How EAST Works

Pytra does not convert Python code directly to the target language. Instead, it goes through an intermediate representation called **EAST** (Extended AST). This page walks through how simple Python code is transformed through EAST1, EAST2, and EAST3.

## Overview

```
  add.py (Python source)
      |
      v  parse
  add.py.east1 (types unresolved, Python-specific)
      |
      v  resolve
  add.east2 (types resolved, language-independent)
      |
      v  compile
  add.east3 (instruction-level, optimizable)
      |
      v  emit
  add.cpp / add.go / add.rs / ...
```

Each stage outputs a JSON file. Since they are human-readable, you can inspect what is happening at each step.

## Example: A Simple Function

```python
def double(x: int) -> int:
    return x * 2

if __name__ == "__main__":
    print(double(21))
```

### EAST1 (after parse)

parse only performs syntactic analysis. Type annotations are preserved exactly as written in the source.

```
FunctionDef
  name: "double"
  args: [{name: "x", annotation: "int"}]    <- remains "int" (not yet int64)
  return_type: "int"                         <- remains "int"
  body:
    Return
      value: BinOp(left: Name("x"), op: "Mult", right: Constant(2))
```

Key points:
- `int` stays as `int`. Normalization to `int64` has not happened yet
- Expression types (`resolved_type`) are unknown
- Source line numbers, comments, and blank lines are all preserved
- No information from other files is referenced (each module is independent)

### EAST2 (after resolve)

resolve resolves types and normalizes Python-specific representations into language-independent form.

```
FunctionDef
  name: "double"
  args: [{name: "x", annotation: "int64"}]   <- int normalized to int64
  return_type: "int64"                        <- same
  body:
    Return
      value: BinOp
        left: Name("x", resolved_type: "int64")    <- type resolved
        op: "Mult"
        right: Constant(2, resolved_type: "int64")  <- type resolved
        resolved_type: "int64"                      <- type of entire expression resolved
```

Key points:
- Every expression has a `resolved_type`. Zero `unknown` values remain
- Normalization such as `int` to `int64`, `float` to `float64` is complete
- Syntax transformations like `for x in range(n)` to `ForRange` are performed here
- Cross-module type resolution (referencing function signatures from imports) happens here

### EAST3 (after compile)

compile performs backend-independent instruction lowering.

```
FunctionDef
  name: "double"
  args: [{name: "x", type: "int64", usage: "readonly"}]
  return_type: "int64"
  body:
    Return
      value: BinOp
        left: Name("x", resolved_type: "int64")
        op: "Mult"
        right: Constant(2, resolved_type: "int64")
        resolved_type: "int64"
```

This example is simple enough that it does not differ much from EAST2, but for more complex code:
- Explicit boxing/unboxing instructions (`ObjBox`, `ObjUnbox`)
- `isinstance` lowered to type_id range checks
- `for` loops converted to `ForCore` + `iter_plan`
- Application of `dispatch_mode`

are performed.

## A More Complex Example: isinstance

```python
def describe(val: JsonVal) -> str:
    if isinstance(val, dict):
        return "dict with " + str(len(val)) + " keys"
    return "other"
```

### Changes in EAST2

resolve applies isinstance narrowing:

```
If
  test: Call(isinstance, [Name("val"), Name("dict")])
  body:
    <- here val's resolved_type has changed to dict[str, JsonVal]
    Return
      value: BinOp(...)
        <- method calls like val.len() are type-resolved
```

Inside the body of `if isinstance`, the variable's type is automatically narrowed, so methods can be called without `cast`.

### Changes in EAST3

isinstance is converted to a type_id check:

```
If
  test: pytra_isinstance(val.type_id, DICT_TID)
  body: ...
```

The emitter simply maps this `pytra_isinstance` call to each target language.

## Running Each Stage Individually

For debugging and investigation, you can run each stage individually:

```bash
pytra-cli2 -parse input.py -o input.py.east1
pytra-cli2 -resolve input.py.east1 -o input.east2
pytra-cli2 -compile input.east2 -o input.east3
```

Open the JSON files to see what happened at each stage.

## Summary

| Stage | Input | Output | What It Does |
|---|---|---|---|
| parse | `.py` | `.py.east1` | Syntax analysis only. Types are unresolved |
| resolve | `.py.east1` | `.east2` | Type resolution, normalization, narrowing |
| compile | `.east2` | `.east3` | Instruction lowering (boxing, type_id, iter_plan) |

EAST is JSON, so you can open it in an editor to inspect the contents. When transformation results look wrong, this helps identify which stage caused the problem.

## Detailed Specifications

- [EAST Unified Specification](../spec/spec-east.md)
- [EAST1 Specification](../spec/spec-east1.md)
- [EAST2 Specification](../spec/spec-east2.md)
