"""Extern-marked I/O helper built-ins."""


from pytra.std import extern


@extern
def py_print[T](value: T) -> None:
    print(value)
