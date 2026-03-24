# pytra: builtin-declarations
"""pytra.std.os_path: os.path 関数の宣言（v2 @extern）。"""

from pytra.std import extern

@extern(module="pytra.std.os_path", symbol="join", tag="stdlib.fn.path_join")
def join(a: str, b: str) -> str: ...

@extern(module="pytra.std.os_path", symbol="dirname", tag="stdlib.fn.path_dirname")
def dirname(p: str) -> str: ...

@extern(module="pytra.std.os_path", symbol="basename", tag="stdlib.fn.path_basename")
def basename(p: str) -> str: ...

@extern(module="pytra.std.os_path", symbol="splitext", tag="stdlib.fn.path_splitext")
def splitext(p: str) -> tuple[str, str]: ...

@extern(module="pytra.std.os_path", symbol="abspath", tag="stdlib.fn.path_abspath")
def abspath(p: str) -> str: ...

@extern(module="pytra.std.os_path", symbol="exists", tag="stdlib.fn.path_exists")
def exists(p: str) -> bool: ...
