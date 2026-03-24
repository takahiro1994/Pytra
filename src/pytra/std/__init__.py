"""Python stdlib compatibility modules for Pytra."""


class _ExternMarker:
    """v2 @extern の戻り値。decorator としても変数 extern としても使える。"""
    def __init__(self, module: str = "", symbol: str = "", tag: str = "") -> None:
        self.module = module
        self.symbol = symbol
        self.tag = tag

    def __call__(self, fn=None):
        # @extern(module=...) def f(): ... のとき decorator として呼ばれる
        if fn is not None:
            return fn
        return self


def extern(fn=None, *, module: str = "", symbol: str = "", tag: str = ""):
    """v1: @extern / extern(expr), v2: @extern(module=..., symbol=..., tag=...).

    使い方:
      @extern                          # v1 decorator
      @extern(module=..., symbol=..., tag=...)  # v2 decorator
      x = extern(expr)                 # v1 変数 extern
      x = extern(module=..., symbol=..., tag=...)  # v2 変数 extern
    """
    if fn is not None and module == "" and symbol == "" and tag == "":
        # v1: @extern or extern(expr)
        return fn
    # v2: キーワード引数あり
    marker = _ExternMarker(module=module, symbol=symbol, tag=tag)
    if fn is not None:
        # extern(expr, module=...) — 変数 extern with fallback value
        return fn
    return marker


def abi(*, args=None, ret="default"):
    def deco(fn):
        return fn

    return deco


def template(*params):
    def deco(fn):
        return fn

    return deco
