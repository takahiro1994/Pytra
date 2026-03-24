# pytra: builtin-declarations
"""pytra.std.math: 数学関数の宣言（v2 extern）。"""

from pytra.std import extern_fn, extern_var

pi: float = extern_var(module="pytra.std.math", symbol="pi", tag="stdlib.symbol.pi")
e: float = extern_var(module="pytra.std.math", symbol="e", tag="stdlib.symbol.e")

@extern_fn(module="pytra.std.math", symbol="sqrt", tag="stdlib.method.sqrt")
def sqrt(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="sin", tag="stdlib.method.sin")
def sin(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="cos", tag="stdlib.method.cos")
def cos(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="tan", tag="stdlib.method.tan")
def tan(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="exp", tag="stdlib.method.exp")
def exp(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="log", tag="stdlib.method.log")
def log(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="log10", tag="stdlib.method.log10")
def log10(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="fabs", tag="stdlib.method.fabs")
def fabs(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="floor", tag="stdlib.method.floor")
def floor(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="ceil", tag="stdlib.method.ceil")
def ceil(x: float) -> float: ...

@extern_fn(module="pytra.std.math", symbol="pow", tag="stdlib.method.pow")
def pow(x: float, y: float) -> float: ...
