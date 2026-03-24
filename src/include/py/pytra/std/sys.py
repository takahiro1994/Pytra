# pytra: builtin-declarations
"""pytra.std.sys: sys モジュールの宣言（v2 @extern）。"""

from pytra.std import extern

argv: list[str] = extern(module="pytra.std.sys", symbol="argv", tag="stdlib.symbol.argv")
path: list[str] = extern(module="pytra.std.sys", symbol="path", tag="stdlib.symbol.path")
stderr: str = extern(module="pytra.std.sys", symbol="stderr", tag="stdlib.symbol.stderr")
stdout: str = extern(module="pytra.std.sys", symbol="stdout", tag="stdlib.symbol.stdout")

@extern(module="pytra.std.sys", symbol="exit", tag="stdlib.fn.exit")
def exit(code: int = 0) -> None: ...

@extern(module="pytra.std.sys", symbol="set_argv", tag="stdlib.fn.set_argv")
def set_argv(values: list[str]) -> None: ...

@extern(module="pytra.std.sys", symbol="set_path", tag="stdlib.fn.set_path")
def set_path(values: list[str]) -> None: ...

@extern(module="pytra.std.sys", symbol="write_stderr", tag="stdlib.fn.write_stderr")
def write_stderr(text: str) -> None: ...

@extern(module="pytra.std.sys", symbol="write_stdout", tag="stdlib.fn.write_stdout")
def write_stdout(text: str) -> None: ...
