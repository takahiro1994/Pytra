<a href="../../ja/progress/emitter-hardcode-lint.md">
  <img alt="日本語で読む" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# Emitter hardcode violation matrix

> Machine-generated file. Run `python3 tools/check/check_emitter_hardcode_lint.py` to update.
> Generated at: 2026-03-30T16:04:20
> [Links](./index.md)

Matrix of grep-detected violations where the emitter hardcodes module names, runtime symbols, or class names instead of using EAST3 data.
Fewer violations means the emitter is more faithfully following the EAST3 source of truth.

| Icon | Meaning |
|---|---|
| 🟩 | No violations |
| 🟥 | Violations found (see details below) |
| ⬜ | Not implemented (no emitter in toolchain2) |

> **js** shares the **ts** emitter and has no separate implementation; the js column mirrors ts results.

| Category | cpp | rs | cs | ps1 | js | ts | dart | go | java | swift | kotlin | ruby | lua | scala | php | nim | julia | zig |
|--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| module name | 🟩 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟥 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| runtime symbol | 🟥 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟥 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| target const | 🟩 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| prefix match | 🟩 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| class name | 🟥 | 🟥 | 🟥 | ⬜ | 🟩 | 🟩 | ⬜ | 🟥 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Python syntax | 🟩 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| type_id | 🟥 | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **🟩 PASS** | 4 | 6 | 6 | — | 7 | 7 | — | 4 | 7 | — | — | — | — | — | — | — | — | — |
| **🟥 FAIL** | 3 | 1 | 1 | — | — | — | — | 3 | — | — | — | — | — | — | — | — | — | — |
| **⬜ Not impl.** | — | — | — | 7 | — | — | 7 | — | — | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |

## Details

### class_name / cpp (3)

```
src/toolchain2/emit/cpp/emitter.py:73: "BaseException", "Exception", "ValueError", "TypeError", "IndexError",
src/toolchain2/emit/cpp/emitter.py:1324: if attr == "add_argument" and owner_type == "ArgumentParser":
src/toolchain2/emit/cpp/emitter.py:2717: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError") or rc == "s
```

### class_name / cs (1)

```
src/toolchain2/emit/cs/emitter.py:295: type_name = "Exception"
```

### class_name / go (19)

```
src/toolchain2/emit/go/emitter.py:107: "ArgumentParser",
src/toolchain2/emit/go/emitter.py:681: "Exception": (10, 15),
src/toolchain2/emit/go/emitter.py:731: "Exception",
src/toolchain2/emit/go/emitter.py:1317: if op == "Div" and left_rt == "Path" and right_rt == "str":
src/toolchain2/emit/go/emitter.py:2314: if fn_name in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError"):
src/toolchain2/emit/go/emitter.py:2787: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError"):
src/toolchain2/emit/go/emitter.py:4111: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4152: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4172: if return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4507: if return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4770: elif base != "" and base not in ("object", "Exception", "BaseException"):
src/toolchain2/emit/go/emitter.py:5302: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5331: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5422: elif ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5544: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5551: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5613: elif ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5616: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5631: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError") or rc == "s
```

### class_name / rs (1)

```
src/toolchain2/emit/rs/emitter.py:653: if obj_type == "Path" and attr in ("name", "stem", "suffix"):
```

### module_name / go (6)

```
src/toolchain2/emit/go/emitter.py:1200: ctx.imports_needed.add("math")
src/toolchain2/emit/go/emitter.py:1203: ctx.imports_needed.add("math")
src/toolchain2/emit/go/emitter.py:1360: ctx.imports_needed.add("math")
src/toolchain2/emit/go/emitter.py:5057: ctx.imports_needed.add("os")
src/toolchain2/emit/go/emitter.py:5063: ctx.imports_needed.add("os")
src/toolchain2/emit/go/emitter.py:5078: ctx.imports_needed.add("os")
```

### runtime_symbol / cpp (1)

```
src/toolchain2/emit/cpp/emitter.py:1539: if rc in ("py_print", "py_len") and len(arg_strs) >= 1:
```

### runtime_symbol / go (2)

```
src/toolchain2/emit/go/emitter.py:2447: if dispatch == "py_print" or bn == "print":
src/toolchain2/emit/go/emitter.py:2451: if dispatch == "py_len" or bn == "len":
```

### type_id / cpp (1)

```
src/toolchain2/emit/cpp/emitter.py:2122: if tid == "" and expected_name.startswith("PYTRA_TID_"):
```
