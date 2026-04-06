# P0-WITH-CONTEXT-MANAGER: with 文を __enter__ / __exit__ プロトコルで実装する

最終更新: 2026-04-06

## 背景

Python の `with` 文は context manager プロトコル（`__enter__` / `__exit__`）に基づく。現状の Pytra は:

- `With` ノードを EAST3 に出力するが、`__enter__` / `__exit__` の呼び出し情報を付与していない
- `open()` の戻り値を Python に存在しない架空の型名 `PyFile` としてハードコードしている
- 各言語の emitter が `With` を個別に（または未実装で）扱っている

### 現状の問題

1. **`PyFile` は架空の型**。Python の `open()` は mode に応じて `io.TextIOWrapper` / `io.BufferedWriter` / `io.BufferedReader` を返す
2. **`__enter__` / `__exit__` が resolve されていない**。emitter が `With` を構造変換する必要があり、emitter guide 違反になる
3. **例外安全が保証されない**。`__exit__` の呼び出しが emitter 任せで契約がない

### fixture

以下の fixture が追加済み:

- `test/fixture/source/py/control/with_context_manager.py` — ユーザー定義クラスの `__enter__` / `__exit__` 呼び出し順序 + 例外安全の検証
- `test/fixture/source/py/control/with_statement.py` — `with open()` のファイル I/O

## 方針

### Phase 1: resolve / compile で `With` を lowering する

`With` ノードを compile パスで以下の構造に lowering する:

```
# Python
with expr as v:
    body

# lowered EAST3（疑似）
__ctx = expr
v = __ctx.__enter__()
Try:
  body: [body]
  finally: [__ctx.__exit__()]
```

これにより `With` ノードは EAST3 から消え、emitter は `Try` + `AnnAssign` + `Call` という既存ノードだけを扱う。

**ただし**、`With` ノードを残して metadata を付与する方式も検討する。理由: C# の `using`、Java の `try-with-resources`、Go の `defer`、Julia の `do` 構文など、言語固有の構文に変換できる情報を保持するため。

→ **採用方式: `With` ノードを EAST3 に残し、`__enter__` / `__exit__` の解決済み情報を metadata として付与する。CommonRenderer がデフォルトの try/finally + hoist 変換を提供し、言語固有の構文がある emitter はオーバーライドする。**

### Phase 2: CommonRenderer にデフォルト変換を実装する

`src/toolchain/emit/common/code_emitter.py` の CommonRenderer に `With` のデフォルト変換を追加:

```
# CommonRenderer のデフォルト出力（try/finally + hoist）
{ctx_type} __ctx = {context_expr};     // hoist
{var_type} {var_name} = __ctx.__enter__();
try {
    {body}
} finally {
    __ctx.__exit__();
}
```

言語ごとのオーバーライド例:

| 言語 | 変換先 | オーバーライド |
|------|--------|--------------|
| C++ | try/finally + hoist（デフォルト） | 不要 |
| C# | `using (var v = expr) { }` | 要 |
| Java | `try (var v = expr) { }` | 要 |
| Go | `defer` + 変数宣言 | 要 |
| Swift | `defer { v.close() }` | 要 |
| Rust | `drop`（所有権で自動） | 要 |
| Julia | `open(path) do f ... end` 等 | 要 |
| TS/JS, Lua, PHP, Ruby, Nim, Zig, PS1 | try/finally + hoist（デフォルト） | 不要 |

### Phase 3: `PyFile` を廃止し、正しい型に置き換える

`src/pytra/built_in/io.py` は作成済み。Python の `open()` が返す型を `@extern class` で定義:

| クラス | 継承 | 用途 |
|--------|------|------|
| `IOBase` | — | 基底クラス。`close` / `__enter__` / `__exit__` を持つ |
| `TextIOWrapper` | `IOBase` | text mode (`"r"`, `"w"`, `"a"`)。`read() -> str` / `write(str) -> int` |
| `BufferedWriter` | `IOBase` | binary write (`"wb"`, `"ab"`)。`write(bytes) -> int` |
| `BufferedReader` | `IOBase` | binary read (`"rb"`)。`read() -> bytes` |

`open()` は mode が静的に判定できない場合でも `IOBase` を返せば `__enter__` / `__exit__` / `close` が呼べる。mode がリテラルなら具象型に narrow 可能だが、それは最適化の話。`mut[T]` 注釈は `containers.py` と同じ規約。

### 検証済み: `@extern class` の継承は resolve で動く

- `_lookup_method_sig` は `_iter_class_hierarchy` でクラス階層を辿る → `TextIOWrapper` から `IOBase.__enter__` が見つかる
- `ClassSig.bases` は EAST1 経由のメインパスで取得される
- runtime 側で継承関係を持つ必要はない。resolve が型階層を理解していれば emitter は metadata だけ見る

### `io.py` を registry に載せるための作業

`containers.py` は `_overlay_container_mutability_from_source` で直接 Python source を読む特別扱い。`io.py` も同じ方式にするか、EAST1 を生成して `src/runtime/east/built_in/` に配置するかの二択。

overlay パーサー（`builtin_registry.py:266-274`）は現在基底クラス名を切り捨てているので、`io.py` の継承関係（`TextIOWrapper(IOBase)`）を扱うには overlay パーサーの拡張が必要。

残作業:
1. `io.py` を registry に載せる経路を用意する（overlay パーサー拡張 or EAST1 配置）
2. overlay パーサーで基底クラス名を `ClassSig.bases` に反映する
3. resolver の `open()` ハードコードを修正し、mode 引数に応じて `TextIOWrapper` / `BufferedWriter` / `BufferedReader`（またはデフォルト `IOBase`）を返すように変更する
4. resolver の `PyFile` メソッドハードコード（`read` / `write` / `close`）を削除し、`built_in/io.py` の定義から解決する
5. EAST3 golden の `resolved_type: "PyFile"` を全て再生成する

### Phase 4: 全言語 parity

`with_context_manager` + `with_statement` fixture で全言語 parity PASS を確認。

## 依存関係

- Phase 1 は resolve/compile（インフラ）の修正
- Phase 2 は CommonRenderer（インフラ）+ 各言語 emitter
- Phase 3 は resolver + built_in 定義（インフラ）
- Phase 4 は全言語 backend

## 注意事項

- compile で `With` を try/finally に完全展開してしまうと、C#/Java/Go 等の言語固有構文への変換情報が失われる。`With` ノードを残して metadata を付与する方式を採用する
- CommonRenderer のデフォルト変換（try/finally + hoist）は C++ を含む多数の言語で使えるため、各 emitter の実装コストは最小
- `__enter__` の戻り値が `self` 以外のケースも Python では合法だが、当面は `self` を返すパターンのみをサポートし、fixture で検証する
