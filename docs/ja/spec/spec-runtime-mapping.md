# runtime mapping.json 仕様

最終更新: 2026-03-25

## 1. 目的

`mapping.json` は、EAST3 の `runtime_call` / `runtime_symbol` をターゲット言語の関数名に写像するための設定ファイルである。各言語の runtime ディレクトリに配置し、`CodeEmitter` 基底クラスが読み込む。

## 2. 配置

```
src/runtime/<lang>/mapping.json
```

例:
- `src/runtime/go/mapping.json`
- `src/runtime/cpp/mapping.json`（将来）

## 3. JSON フォーマット

```json
{
  "builtin_prefix": "<prefix>",
  "calls": {
    "<runtime_call>": "<target_function_name>",
    ...
  },
  "skip_modules": [
    "<module_id_prefix>",
    ...
  ]
}
```

### 3.1 `builtin_prefix`

型: `string`
必須: はい

`calls` に一致しない `runtime_call` に対して自動的に付与される prefix。

例: `"py_"` → `runtime_call: "abs"` が `calls` になければ `py_abs` に解決される。

### 3.2 `calls`

型: `object`（key: string, value: string）
必須: はい

EAST3 の `runtime_call` または `builtin_name` をターゲット言語の関数名に写像する。

key は以下のいずれか:
- `runtime_call` の値（例: `"py_print"`, `"static_cast"`, `"list.append"`）
- `builtin_name` の値（例: `"print"`, `"len"`）

value は以下のいずれか:
- ターゲット言語の関数名（例: `"py_print"`, `"py_str_strip"`）
- 特殊マーカー（emitter が特別処理する。例: `"__CAST__"`, `"__LIST_APPEND__"`）

### 3.3 `skip_modules`

型: `array` of `string`
必須: はい

emit をスキップするモジュール ID の prefix リスト。これらのモジュールは runtime が native 実装を提供するため、トランスパイル結果を出力しない。

例:
```json
["pytra.built_in.", "pytra.std.", "pytra.utils.", "pytra.core."]
```

## 4. 解決優先順位

`CodeEmitter.resolve_runtime_call()` は以下の優先順位で解決する:

1. `calls` に `runtime_call` の exact match がある → その値を返す
2. `calls` に `builtin_name` の exact match がある → その値を返す
3. `adapter_kind == "builtin"` → `builtin_prefix + builtin_name`
4. `adapter_kind == "extern_delegate"` → `builtin_name`（prefix なし）
5. フォールバック → `builtin_prefix + runtime_call`

## 5. 特殊マーカー

`calls` の value に特殊マーカーを使うことで、emitter に言語固有の特殊処理を指示できる。

| マーカー | 意味 | 例 |
|---|---|---|
| `__CAST__` | 言語固有の型キャスト構文で出力 | Go: `int64(x)`, C++: `static_cast<int64_t>(x)` |
| `__LIST_APPEND__` | 言語固有の append 構文で出力 | Go: `x = append(x, v)` |
| `__LIST_POP__` | 言語固有の pop 構文で出力 | Go: スライス操作 |
| `__DICT_GET__` | 言語固有の dict アクセスで出力 | Go: `x, ok := m[key]` |
| `__SET_ADD__` | 言語固有の set 追加で出力 | Go: `m[key] = true` |
| `__MAKE_BYTES__` | 言語固有の bytes 生成で出力 | Go: `make([]byte, n)` |
| `__PANIC__` | 言語固有の例外/パニックで出力 | Go: `panic(msg)` |

特殊マーカーの解釈は emitter の責務。mapping.json はマーカー文字列を定義するだけ。

## 6. 命名ルール

`calls` の value（ターゲット関数名）は以下の命名ルールに従う:

| カテゴリ | パターン | 例 |
|---|---|---|
| built-in 関数 | `py_<name>` | `py_len`, `py_print`, `py_abs` |
| str メソッド | `py_str_<method>` | `py_str_strip`, `py_str_join` |
| list メソッド | `py_list_<method>` | `py_list_append`, `py_list_pop` |
| dict メソッド | `py_dict_<method>` | `py_dict_get`, `py_dict_keys` |
| set メソッド | `py_set_<method>` | `py_set_add`, `py_set_discard` |
| stdlib 関数 | `py_<module>_<name>` | `py_math_sqrt`, `py_time_perf_counter` |

- `py_` prefix は「Python frontend 由来の意味論」を示す
- **ベース名は全言語共通**。各言語は必要に応じて case を変換する
- ターゲット言語にネイティブの等価関数がある場合は、mapping で直接そちらに写像してよい
- ベース名がターゲット言語の予約語と衝突した場合は、末尾に `_` を付けて回避する

詳細: `docs/ja/plans/plan-pipeline-redesign.md` §3.4

## 7. 実装

- `toolchain2/emit/common/code_emitter.py` の `load_runtime_mapping()` が読み込む
- `RuntimeMapping` dataclass に格納される
- `resolve_runtime_call()` が解決に使用する
