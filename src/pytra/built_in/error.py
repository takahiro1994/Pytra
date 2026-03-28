"""Pytra built-in exception classes.

These classes are transpiled through the standard pipeline to all target
languages.  No hand-written runtime exception types are needed.

Exception hierarchy:

    PytraError
    ├── ValueError
    ├── RuntimeError
    ├── FileNotFoundError
    ├── PermissionError
    ├── TypeError
    ├── IndexError
    ├── KeyError
    └── OverflowError

Users can define custom exceptions by inheriting from any of the above.
"""


class PytraError:
    msg: str

    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class BaseException(PytraError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class Exception(BaseException):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class ValueError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class RuntimeError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class FileNotFoundError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class PermissionError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class TypeError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class IndexError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class KeyError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class NameError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class NotImplementedError(RuntimeError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class OverflowError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
