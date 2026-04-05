<a href="../../en/guide/east-overview.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# EAST の仕組み

Pytra は Python コードをいきなりターゲット言語に変換するのではなく、**EAST**（Extended AST）という中間表現を経由します。このページでは、簡単な Python コードが EAST1 → EAST2 → EAST3 と変換される過程を追います。

## 全体像

```
  add.py（Python ソース）
      │
      ▼  parse
  add.py.east1（型未解決、Python 固有）
      │
      ▼  resolve
  add.east2（型確定、言語非依存）
      │
      ▼  compile
  add.east3（命令化済み、最適化可能）
      │
      ▼  emit
  add.cpp / add.go / add.rs / ...
```

各段は JSON ファイルを出力します。人間が読めるので、何が起きているか確認できます。

## 例: 簡単な関数

```python
def double(x: int) -> int:
    return x * 2

if __name__ == "__main__":
    print(double(21))
```

### EAST1（parse 後）

parse は構文解析だけを行います。型注釈はソースに書かれたまま保持されます。

```
FunctionDef
  name: "double"
  args: [{name: "x", annotation: "int"}]    ← "int" のまま（int64 にはまだならない）
  return_type: "int"                         ← "int" のまま
  body:
    Return
      value: BinOp(left: Name("x"), op: "Mult", right: Constant(2))
```

ポイント:
- `int` は `int` のまま。`int64` への正規化はまだ起きない
- 式の型（`resolved_type`）は不明
- ソースの行番号、コメント、空行が全て保持される
- 他のファイルの情報は一切参照しない（モジュール単位で独立）

### EAST2（resolve 後）

resolve は型を解決し、Python 固有の表現を言語非依存に正規化します。

```
FunctionDef
  name: "double"
  args: [{name: "x", annotation: "int64"}]   ← int → int64 に正規化
  return_type: "int64"                        ← 同上
  body:
    Return
      value: BinOp
        left: Name("x", resolved_type: "int64")    ← 型が確定
        op: "Mult"
        right: Constant(2, resolved_type: "int64")  ← 型が確定
        resolved_type: "int64"                      ← 式全体の型も確定
```

ポイント:
- 全ての式に `resolved_type` が付く。`unknown` はゼロ
- `int` → `int64`、`float` → `float64` 等の正規化が完了
- `for x in range(n)` → `ForRange` への構文変換もここで行われる
- cross-module の型解決（import 先の関数シグネチャ参照）もここ

### EAST3（compile 後）

compile は backend 非依存の命令化を行います。

```
FunctionDef
  name: "double"
  args: [{name: "x", type: "int64", usage: "readonly"}]
  return_type: "int64"
  body:
    Return
      value: BinOp
        left: Name("x", resolved_type: "int64")
        op: "Mult"
        right: Constant(2, resolved_type: "int64")
        resolved_type: "int64"
```

この例は単純なので EAST2 と大きく変わりませんが、複雑なコードでは:
- boxing/unboxing の明示命令（`ObjBox`, `ObjUnbox`）
- `isinstance` の type_id 判定命令
- `for` ループの `ForCore` + `iter_plan` への変換
- `dispatch_mode` の適用

が行われます。

## もう少し複雑な例: isinstance

```python
def describe(val: JsonVal) -> str:
    if isinstance(val, dict):
        return "dict with " + str(len(val)) + " keys"
    return "other"
```

### EAST2 での変化

resolve が isinstance ナローイングを適用します:

```
If
  test: Call(isinstance, [Name("val"), Name("dict")])
  body:
    ← ここでは val の resolved_type が dict[str, JsonVal] に変わっている
    Return
      value: BinOp(...)
        ← val.len() 等のメソッド呼び出しが型解決済み
```

`if isinstance` の body 内で変数の型が自動的に絞り込まれるので、`cast` なしでメソッドが呼べます。

### EAST3 での変化

isinstance が type_id 判定に変換されます:

```
If
  test: pytra_isinstance(val.type_id, DICT_TID)
  body: ...
```

emitter はこの `pytra_isinstance` 呼び出しを各言語に写像するだけです。

## 各段を個別に実行する

デバッグや調査のために、各段を個別に実行できます:

```bash
pytra-cli -parse input.py -o input.py.east1
pytra-cli -resolve input.py.east1 -o input.east2
pytra-cli -compile input.east2 -o input.east3
```

JSON ファイルを開いて、各段で何が起きたか確認してみてください。

## まとめ

| 段 | 入力 | 出力 | 何をするか |
|---|---|---|---|
| parse | `.py` | `.py.east1` | 構文解析のみ。型は未解決 |
| resolve | `.py.east1` | `.east2` | 型解決、正規化、ナローイング |
| compile | `.east2` | `.east3` | 命令化（boxing, type_id, iter_plan） |

EAST は JSON なので、エディタで開いて中身を確認できます。変換結果がおかしいときは、どの段で問題が起きたか特定する手がかりになります。

## 詳しい仕様

- [EAST 統合仕様](../spec/spec-east.md)
- [EAST1 仕様](../spec/spec-east1.md)
- [EAST2 仕様](../spec/spec-east2.md)
