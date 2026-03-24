# pytra: builtin-declarations
"""pytra.std.time: 時間関数の宣言（v2 @extern）。

spec: docs/ja/spec/spec-builtin-functions.md §10
"""

from pytra.std import extern

@extern(module="pytra.std.time", symbol="perf_counter", tag="stdlib.fn.perf_counter")
def perf_counter() -> float: ...
