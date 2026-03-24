# pytra: builtin-declarations
"""Python built-in 関数の宣言。

resolve がシグネチャを参照して型解決する。emit 対象外。

spec: docs/ja/spec/spec-builtin-functions.md
"""

from pytra.std import extern_fn, template
from pytra.types import Obj


# ---------------------------------------------------------------------------
# §3.1 dunder 委譲型
# ---------------------------------------------------------------------------

@extern_fn(module="pytra.core.py_runtime", symbol="len", tag="core.len")
def len(x: Obj) -> int: ...

@extern_fn(module="pytra.core.py_runtime", symbol="str", tag="cast.str")
def str(x: Obj) -> str: ...

@extern_fn(module="pytra.core.py_runtime", symbol="bool", tag="cast.bool")
def bool(x: Obj) -> bool: ...

@extern_fn(module="pytra.core.py_runtime", symbol="int", tag="cast.int")
def int(x: Obj) -> int: ...

@extern_fn(module="pytra.core.py_runtime", symbol="float", tag="cast.float")
def float(x: Obj) -> float: ...

@extern_fn(module="pytra.core.py_runtime", symbol="repr", tag="cast.repr")
def repr(x: Obj) -> str: ...


# ---------------------------------------------------------------------------
# §3.2 スタンドアロン型
# ---------------------------------------------------------------------------

@extern_fn(module="pytra.built_in.io_ops", symbol="py_print", tag="core.print")
def print(*args: Obj) -> None: ...

@extern_fn(module="pytra.core.py_runtime", symbol="isinstance", tag="type.isinstance")
def isinstance(x: Obj, t: type) -> bool: ...

@extern_fn(module="pytra.core.py_runtime", symbol="issubclass", tag="type.issubclass")
def issubclass(cls: type, parent: type) -> bool: ...

@extern_fn(module="pytra.core.py_runtime", symbol="py_round", tag="math.round")
def round(x: float, ndigits: int = 0) -> int: ...

@extern_fn(module="pytra.core.py_runtime", symbol="py_abs", tag="math.abs")
def abs(x: int) -> int: ...

@extern_fn(module="pytra.built_in.scalar_ops", symbol="py_ord", tag="cast.ord")
def ord(c: str) -> int: ...

@extern_fn(module="pytra.built_in.scalar_ops", symbol="py_chr", tag="cast.chr")
def chr(i: int) -> str: ...


# ---------------------------------------------------------------------------
# §3.3 ジェネリック型
# ---------------------------------------------------------------------------

@template("T")
@extern_fn(module="pytra.built_in.numeric_ops", symbol="py_min", tag="math.min")
def min(*args: T) -> T: ...

@template("T")
@extern_fn(module="pytra.built_in.numeric_ops", symbol="py_max", tag="math.max")
def max(*args: T) -> T: ...

@template("T")
@extern_fn(module="pytra.built_in.iter_ops", symbol="py_sorted", tag="iter.sorted")
def sorted(x: list[T]) -> list[T]: ...

@template("T")
@extern_fn(module="pytra.built_in.iter_ops", symbol="py_reversed_object", tag="iter.reversed")
def reversed(x: list[T]) -> list[T]: ...

@template("T")
@extern_fn(module="pytra.built_in.iter_ops", symbol="py_enumerate_object", tag="iter.enumerate")
def enumerate(x: list[T], start: int = 0) -> list[tuple[int, T]]: ...

@template("T", "U")
@extern_fn(module="pytra.built_in.zip_ops", symbol="zip", tag="iter.zip")
def zip(a: list[T], b: list[U]) -> list[tuple[T, U]]: ...


# ---------------------------------------------------------------------------
# §3.4 range
# ---------------------------------------------------------------------------

@extern_fn(module="pytra.built_in.sequence", symbol="py_range", tag="iter.range")
def range(stop: int) -> list[int]: ...

@extern_fn(module="pytra.built_in.sequence", symbol="py_range", tag="iter.range")
def range(start: int, stop: int) -> list[int]: ...

@extern_fn(module="pytra.built_in.sequence", symbol="py_range", tag="iter.range")
def range(start: int, stop: int, step: int) -> list[int]: ...
