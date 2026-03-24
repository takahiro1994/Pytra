# pytra: builtin-declarations
"""pytra.std.glob: glob 関数の宣言（v2 extern）。"""

from pytra.std import extern_fn

@extern_fn(module="pytra.std.glob", symbol="glob", tag="stdlib.fn.glob")
def glob(pattern: str) -> list[str]: ...
