# pytra: builtin-declarations
"""pytra.std.time: 時間関数の宣言（v2 extern）。"""

from pytra.std import extern_fn

@extern_fn(module="pytra.std.time", symbol="perf_counter", tag="stdlib.fn.perf_counter")
def perf_counter() -> float: ...
