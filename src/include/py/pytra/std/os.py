# pytra: builtin-declarations
"""pytra.std.os: OS 関数の宣言（v2 @extern）。"""

from pytra.std import extern

@extern(module="pytra.std.os", symbol="getcwd", tag="stdlib.fn.getcwd")
def getcwd() -> str: ...

@extern(module="pytra.std.os", symbol="mkdir", tag="stdlib.fn.mkdir")
def mkdir(p: str, exist_ok: bool = False) -> None: ...

@extern(module="pytra.std.os", symbol="makedirs", tag="stdlib.fn.makedirs")
def makedirs(p: str, exist_ok: bool = False) -> None: ...
