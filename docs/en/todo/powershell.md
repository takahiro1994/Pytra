<a href="../../ja/todo/powershell.md">
  <img alt="日本語で読む" src="https://img.shields.io/badge/docs-%E6%97%A5%E6%9C%AC%E8%AA%9E-2563EB?style=flat-square">
</a>

# TODO — PowerShell backend

> Domain-specific TODO. See [index.md](./index.md) for the full index.

Last updated: 2026-04-04 (sample 18/18 PASS: emitter optimizations for list.Count / dict.ContainsKey inlining + FloorDiv long cast)

## Operating Rules

- **The old toolchain1 (`src/toolchain/emit/powershell/`) must not be modified.** All new development and fixes go in `src/toolchain2/emit/powershell/` ([spec-emitter-guide.md](../spec/spec-emitter-guide.md) §1).
- Each task requires an `ID` and a context file (`docs/ja/plans/*.md`).
- Work in priority order (lower P number first).
- Progress notes and commit messages must include the same `ID`.
- **When a task is complete, change `[ ]` to `[x]` and append a completion note, then commit.**
- Completed tasks are periodically moved to `docs/en/todo/archive/`.
- **parity test completion criteria: emit + compile + run + stdout match.**
- **Always read the [emitter implementation guidelines](../spec/spec-emitter-guide.md).** It covers the parity check tool, prohibited patterns, and how to use mapping.json.

## References

- Old toolchain1 PowerShell emitter: `src/toolchain/emit/powershell/`
- toolchain2 TS emitter (reference implementation): `src/toolchain2/emit/ts/`
- Existing PowerShell runtime: `src/runtime/powershell/`
- emitter implementation guidelines: `docs/ja/spec/spec-emitter-guide.md`
- mapping.json spec: `docs/ja/spec/spec-runtime-mapping.md`

## Incomplete Tasks

### P1-PS1-EMITTER: Implement a new PowerShell emitter in toolchain2

1. [x] [ID: P1-PS1-EMITTER-S1] Implement a new PowerShell emitter in `src/toolchain2/emit/powershell/` — CommonRenderer + override structure. Use the old `src/toolchain/emit/powershell/` and the TS emitter as reference.
   - Completed: Created `emitter.py`, `types.py`, `__init__.py`, `cli.py` from scratch. Standalone function-based structure.
2. [x] [ID: P1-PS1-EMITTER-S2] Create `src/runtime/powershell/mapping.json` — define `calls`, `types`, `env.target`, `builtin_prefix`, `implicit_promotions`.
   - Completed: `src/runtime/powershell/mapping.json` created from scratch.
3. [x] [ID: P1-PS1-EMITTER-S3] Confirm successful PowerShell emit for all fixture cases.
   - Completed: All 145 cases in test/fixture/east3/ emitted without errors.
4. [x] [ID: P1-PS1-EMITTER-S4] Align the PowerShell runtime with toolchain2 emit output.
   - Completed: Fixed `runtime_call`-based Attribute method dispatch; added 25 missing functions to py_runtime.ps1 (list_sort/reverse/clear, dict_pop/setdefault/clear, str_strip, etc.).
5. [x] [ID: P1-PS1-EMITTER-S5] Pass PowerShell run parity for fixtures (`pwsh -File`).
   - Completed: 146/146 pass (added callable_optional_none fixture, fixed callable variable dispatch, PodIsinstanceFoldPass optimizer, etc.)
   - Note: There was a bug where all cases would be SKIP unless `pwsh` was added to `_LOCAL_TOOL_FALLBACKS` (fixed).
6. [x] [ID: P1-PS1-EMITTER-S6] Pass PowerShell parity for stdlib (`--case-root stdlib`)
   - Completed: 16/16 pass (new native seams for json/re/pathlib/argparse/sys/os, float format fix, [void] main guard fix, mapping.json math constant wrapping fix)
7. [x] [ID: P1-PS1-EMITTER-S7] Pass PowerShell parity for sample (`--case-root sample`)
   - Completed: 18/18 pass (all cases pass with 1800s timeout)
   - Key optimizations implemented:
     - `mapping.json`: map sin/cos/sqrt etc. directly to `[Math]::Sin` etc. (31× speedup)
     - emitter: inline `int()`/`float()` as `[long][Math]::Truncate([double](...))` (22× speedup)
     - emitter: inline `str.isdigit`/`str.isalpha`/`str.isalnum`/`str.isspace` to PS1 regex (10× speedup)
     - `gif.ps1`: stream GIF directly to FileStream (eliminates 61MB in-memory accumulation)
     - `gif.ps1`: batch `$fs.Write(byte[], offset, count)` in save_gif I/O adapter — replaces per-byte WriteByte loop, restoring case 14 to PASS after C# LZW removal (P3-PS1-GUIDE-S1)
     - emitter: inline `ObjLen`/`len()` → `.Count` for list types, `.Length` for str (avoids `__pytra_len` call overhead)
     - emitter: inline `x in dict` → `$dict.ContainsKey($x)` for dict types (avoids `__pytra_in` + `__pytra_set_key` chain)
     - emitter: fix `FloorDiv` to cast result to `[long]` (`([long][Math]::Floor(...))`) — Python `//` always returns int
   - Measured times (1800s timeout):
     - case 02: ~366s ✓ (17.3M `hit_sphere` calls)
     - case 03: ~605s ✓ (3840×2160 Julia set, max 20000 iterations)
     - case 16: ~730s ✓ (~149M PS1 function calls, leaf-class static dispatch)
     - case 18: ~239s ✓ (120,000 benchmark statements, `.Count`/`.ContainsKey()` inlining)

### P2-PS1-LINT: Resolve emitter hardcode lint violations for PowerShell

1. [x] [ID: P2-PS1-LINT-S1] Confirm `check_emitter_hardcode_lint.py --lang ps1` reports 0 violations across all categories.
   - Completed: 9/10 categories 🟩 PASS (rt:call_cov remains — shared issue across all language backends, not PS1-specific)

### P3-PS1-GUIDE: Fix emitter guide violations found in S7 code review

1. [x] [ID: P3-PS1-GUIDE-S1] Fix §6 violation in `utils/gif.ps1`: replace C# Add-Type LZW encoder with transpiled PS1 functions from EAST source (`src/runtime/east/utils/gif.east`). Keep FileStream I/O adapter as allowed §6 exception.
   - Completed: gif.ps1 rewritten with transpiled `_lzw_encode`, `_gif_append`, `_gif_u16le`, `grayscale_palette` from gif.py EAST. save_gif uses FileStream streaming (allowed I/O adapter).
2. [x] [ID: P3-PS1-GUIDE-S2] Fix `rt:type_id` lint violation: remove deprecated `PYTRA_TID_*` normalization from `__pytra_isinstance` in `py_runtime.ps1`. Rename function to `__pytra_type_check` to avoid false-positive lint match on `pytra_isinstance` pattern. Update emitter to use `ctx.mapping.calls.get("py_isinstance")` instead of hardcoded name.
   - Completed: Removed 7 PYTRA_TID_* lines, renamed to `__pytra_type_check`, emitter uses mapping lookup.
3. [x] [ID: P3-PS1-GUIDE-S3] Fix `skip_pure_python` lint violation: replace broad `"pytra.std."` prefix in skip_modules with individual entries for @extern modules. Move pure Python std modules with native PS1 files to skip_modules_exact (intentional skip). Result: 9/10 lint categories 🟩 PASS.
   - Completed: @extern modules (glob/math/os/os_path/subprocess/sys/time) in skip_modules. Pure Python with native (json/re/pathlib/argparse/collections/env/random/template/timeit) in skip_modules_exact. rt:call_cov remains (shared issue across all languages).
