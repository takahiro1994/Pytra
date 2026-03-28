<a href="../../en/tutorial/exception.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# 例外処理

このページでは、Pytra での例外処理（`raise` / `try` / `except` / `finally`）の使い方を説明します。

## 基本: raise と try/except

Python と同じ構文でエラーを投げたり捕捉したりできます。

```python
from pytra.built_in.error import ValueError

def parse_int(s: str) -> int:
    if not s.isdigit():
        raise ValueError("not a number: " + s)
    return int(s)

if __name__ == "__main__":
    try:
        x = parse_int("abc")
        print(x)
    except ValueError as e:
        print("error: " + e.msg)
```

出力:

```text
error: not a number: abc
```

## 使える例外型

Pytra の組み込み例外は `pytra.built_in.error` に定義されています。

```python
from pytra.built_in.error import (
    PytraError,          # 全例外の基底
    ValueError,          # 値エラー
    RuntimeError,        # 実行時エラー
    FileNotFoundError,   # ファイル未検出
    PermissionError,     # 権限エラー
    TypeError,           # 型エラー
    IndexError,          # インデックス範囲外
    KeyError,            # キー未検出
    OverflowError,       # オーバーフロー
)
```

継承関係:

```
PytraError
├── ValueError
├── RuntimeError
├── FileNotFoundError
├── PermissionError
├── TypeError
├── IndexError
├── KeyError
└── OverflowError
```

## 自分で例外を定義する

組み込み例外を継承して、フィールドを持つカスタム例外を作れます。

```python
from pytra.built_in.error import ValueError

class ParseError(ValueError):
    line: int

    def __init__(self, line: int, msg: str) -> None:
        super().__init__(msg)
        self.line = line

def parse(s: str, line: int) -> int:
    if not s.isdigit():
        raise ParseError(line, "not a number: " + s)
    return int(s)

if __name__ == "__main__":
    try:
        x = parse("abc", 42)
    except ParseError as e:
        print("line " + str(e.line) + ": " + e.msg)
```

出力:

```text
line 42: not a number: abc
```

## except は派生クラスも捕捉する

`except ValueError` は `ValueError` だけでなく、その派生クラス（`ParseError` 等）も捕捉します。これは Python と同じ動作です。

```python
try:
    x = parse("abc", 42)    # ParseError が飛ぶ
except ValueError as e:      # ParseError も捕捉される（ValueError の派生だから）
    print("caught: " + e.msg)
```

## 複数の except

```python
from pytra.built_in.error import ValueError, RuntimeError

try:
    data = read_file(path)
except FileNotFoundError as e:
    data = ""
except PermissionError as e:
    raise RuntimeError("no access: " + e.msg)
```

上から順に型を判定し、最初に一致したものが実行されます。

## finally

`finally` ブロックは、正常終了でもエラー終了でも必ず実行されます。

```python
try:
    f = open(path, "wb")
    f.write(data)
except ValueError as e:
    print("error: " + e.msg)
finally:
    f.close()    # 必ず実行される
```

## エラーの伝播

`try/except` で捕捉しなかったエラーは、呼び出し元に自動的に伝播します。

```python
def step1(s: str) -> int:
    return parse_int(s)        # parse_int が raise → そのまま上に飛ぶ

def step2(s: str) -> str:
    x = step1(s)               # step1 の raise → そのまま上に飛ぶ
    return str(x * 2)

if __name__ == "__main__":
    try:
        result = step2("abc")  # ここで捕捉
    except ValueError as e:
        print("caught: " + e.msg)
```

## 全言語で動く

Pytra の例外処理は全18ターゲット言語で動作します。

- **C++, Java, C# 等**（例外がある言語）: ネイティブの `throw` / `try-catch` に変換
- **Go, Rust, Zig**（例外がない言語）: 戻り値ベースのエラー伝播に自動変換

ユーザーが言語の違いを意識する必要はありません。同じ `raise` / `try/except` がどの言語でも動きます。

## 例外型は普通のクラス

Pytra の例外型はただのクラスです。特別な仕組みではありません。

- 単一継承に従う
- フィールドを持てる
- `isinstance` で判定できる（`except` の内部動作）
- `type_id` で効率的に判定される

## まとめ

| やりたいこと | 書き方 |
|---|---|
| エラーを投げる | `raise ValueError("msg")` |
| エラーを捕捉する | `try: ... except ValueError as e: ...` |
| 後始末を保証する | `finally: cleanup()` |
| 自分の例外を定義する | `class MyError(ValueError): ...` |
| 例外を import する | `from pytra.built_in.error import ValueError` |

詳しい仕様は以下を参照してください:
- [例外処理仕様](../spec/spec-exception.md) — 各言語への変換規則、EAST ノード、union_return の詳細
