"""pytra.std.env: 実行環境情報。

Python で直接実行する場合は target = "python"。
変換後のコードでは mapping.json の env.target に置換される。
"""

target: str = "python"
