"""pytra.std.os: extern-marked os subset with Python runtime fallback."""


import os

from pytra.std import extern
from pytra.std import os_path as path


@extern
def getcwd() -> str:
    return os.getcwd()


@extern
def mkdir(p: str, exist_ok: bool = False) -> None:
    if exist_ok and path.exists(p):
        return
    os.mkdir(p)


@extern
def makedirs(p: str, exist_ok: bool = False) -> None:
    os.makedirs(p, exist_ok=exist_ok)
