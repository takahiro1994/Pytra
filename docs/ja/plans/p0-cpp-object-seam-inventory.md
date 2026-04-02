# P0 C++ object seam inventory

最終更新: 2026-04-02

## 目的

`src/runtime/cpp/core/object.h` の `Object<void>` / `using object = Object<void>` を削除する前に、C++ backend に残っている object seam を棚卸しし、どの TODO で消すかを固定する。

## 現状の seam

### 1. EAST / lower 起点

- `src/toolchain2/compile/lower.py`
  - `resolved_type="object"` Boxing
  - iter boundary (`OBJ_ITER_INIT`, `OBJ_ITER_NEXT`)
  - `PYTRA_TID_OBJECT` への変換表

担当:
- `P0-CPP-VARIANT-S10`
- `P0-CPP-VARIANT-S11`

### 2. C++ emitter 起点

- `src/toolchain2/emit/cpp/emitter.py`
  - `Box` / `Unbox` emission
  - `object(...)` boxing path
  - `.as<...>()` / `.unbox<...>()`
  - generic `Callable` bridge `([&](object) -> object { ... })`
  - object fallback container (`dict[str, object]`, `list[object]`, `set[object]`)
  - object-based type narrowing / cast fallback

担当:
- `P0-CPP-VARIANT-S8`
- `P0-CPP-VARIANT-S9`
- `P0-CMN-BOXUNBOX-S1`
- `P0-CMN-BOXUNBOX-S2`

### 3. C++ runtime stdlib seam

- `src/runtime/cpp/std/argparse.{h,cpp}`
  - `Namespace.values: Object<dict<str, object>>`
  - `default_value: object`
- `src/runtime/cpp/std/pathlib.{h,cpp}`
  - `Path(const object&)`
  - `__truediv__(const object&)`
  - `relative_to(const object&)`
- tuple runtime fallback
  - `src/runtime/cpp/built_in/dict_ops.h`
  - `py_at(tuple, idx) -> object`

担当:
- `P0-CPP-VARIANT-S8`
- follow-up runtime parity task if object-free signature migrationが単独で必要なら別起票

### 4. runtime core seam

- `src/runtime/cpp/core/object.h`
  - `Object<void>`
  - `using object = Object<void>`
- `src/runtime/cpp/core/py_types.h`
  - `Object<void>::unbox`
  - POD boxing constructors
- `src/runtime/cpp/built_in/base_ops.h`
  - `py_is_*` / `py_to_string(const object&)`
- `src/runtime/cpp/core/conversions.h`
  - `py_to_int64(const object&)`, `py_to_float64(const object&)`, etc.

担当:
- `P0-CPP-VARIANT-S6B`

## 削除順

1. `P0-CMN-BOXUNBOX-S1/S2` で backend 共通の正規化を入れる
2. `P0-CPP-VARIANT-S8/S9` で C++ emitter の object boxing / unboxing 依存を減らす
3. `P0-CPP-VARIANT-S10/S11` で EAST 側の object 退化を止める
4. runtime stdlib seam が object-free で通ることを確認する
5. `P0-CPP-VARIANT-S6B` で `object.h` 本体を削除する

## 完了条件

- 上記 seam が TODO ID に一対一で紐付いている
- `object.h` 削除前に何を先にやるべきかが TODO だけで判断できる
