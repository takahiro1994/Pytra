# pytra: builtin-declarations
"""pytra.std.subprocess: subprocess 関数の宣言（v2 extern）。"""

from pytra.std import extern_fn


class CompletedProcess:
    returncode: int
    stdout: str
    stderr: str

@extern_fn(module="pytra.std.subprocess", symbol="run", tag="stdlib.fn.subprocess_run")
def run(cmd: list[str], cwd: str = "", capture_output: bool = False, env: dict[str, str] = {}) -> CompletedProcess: ...
