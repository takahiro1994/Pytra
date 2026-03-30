<a href="../../ja/progress/emitter-hardcode-lint.md">
  <img alt="日本語で読む" src="https://img.shields.io/badge/docs-日本語-DC2626?style=flat-square">
</a>

# Emitter hardcode violation matrix

> Machine-generated file. Run `python3 tools/check/check_emitter_hardcode_lint.py` to update.
> Generated at: 2026-03-30T13:15:11
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
| module name | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟥 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| runtime symbol | 🟥 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟥 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| target const | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| prefix match | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| class name | 🟥 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟥 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Python syntax | 🟩 | 🟩 | ⬜ | ⬜ | 🟩 | 🟩 | ⬜ | 🟩 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| **🟩 PASS** | 4 | 6 | — | — | 6 | 6 | — | 3 | — | — | — | — | — | — | — | — | — | — |
| **🟥 FAIL** | 2 | — | — | — | — | — | — | 3 | — | — | — | — | — | — | — | — | — | — |
| **⬜ Not impl.** | — | — | 6 | 6 | — | — | 6 | — | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |

## Details

### class_name / cpp (3)

```
src/toolchain2/emit/cpp/emitter.py:73: "BaseException", "Exception", "ValueError", "TypeError", "IndexError",
src/toolchain2/emit/cpp/emitter.py:1324: if attr == "add_argument" and owner_type == "ArgumentParser":
src/toolchain2/emit/cpp/emitter.py:2717: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError") or rc == "s
```

### class_name / go (19)

```
src/toolchain2/emit/go/emitter.py:105: "ArgumentParser",
src/toolchain2/emit/go/emitter.py:656: "Exception": (10, 15),
src/toolchain2/emit/go/emitter.py:705: "Exception",
src/toolchain2/emit/go/emitter.py:1284: if op == "Div" and left_rt == "Path" and right_rt == "str":
src/toolchain2/emit/go/emitter.py:2265: if fn_name in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError"):
src/toolchain2/emit/go/emitter.py:2736: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError"):
src/toolchain2/emit/go/emitter.py:4028: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4069: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4089: if return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4424: if return_type == "Exception":
src/toolchain2/emit/go/emitter.py:4687: elif base != "" and base not in ("object", "Exception", "BaseException"):
src/toolchain2/emit/go/emitter.py:5191: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5220: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5311: elif ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5433: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5440: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5502: elif ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5505: if ctx.current_return_type == "Exception":
src/toolchain2/emit/go/emitter.py:5520: if bn in ("BaseException", "Exception", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError") or rc == "s
```

### module_name / go (6)

```
src/toolchain2/emit/go/emitter.py:1172: ctx.imports_needed.add("math")
src/toolchain2/emit/go/emitter.py:1175: ctx.imports_needed.add("math")
src/toolchain2/emit/go/emitter.py:1327: ctx.imports_needed.add("math")
src/toolchain2/emit/go/emitter.py:4946: ctx.imports_needed.add("os")
src/toolchain2/emit/go/emitter.py:4952: ctx.imports_needed.add("os")
src/toolchain2/emit/go/emitter.py:4967: ctx.imports_needed.add("os")
```

### runtime_symbol / cpp (1)

```
src/toolchain2/emit/cpp/emitter.py:1539: if rc in ("py_print", "py_len") and len(arg_strs) >= 1:
```

### runtime_symbol / go (2)

```
src/toolchain2/emit/go/emitter.py:2396: if dispatch == "py_print" or bn == "print":
src/toolchain2/emit/go/emitter.py:2400: if dispatch == "py_len" or bn == "len":
```
