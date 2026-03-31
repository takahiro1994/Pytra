# 計画: Rust の `in` 演算子を iterable の汎用 contains で処理する (P0-RS-IN-ITERABLE)

## 背景

Python の `in` 演算子は iterable プロトコルに従う汎用演算子:

```python
x in [1, 2, 3]       # list の __contains__
x in (1, 2, 3)        # tuple の __contains__
x in {1, 2, 3}        # set の __contains__
x in "abc"            # str の __contains__
x in range(1000)      # range の __contains__
x in my_iterable      # 任意の iterable
```

現状の Rust emitter / runtime は tuple の `in` を要素数ごとの `PyContains` trait impl で処理している。2要素から12要素まで11個のほぼ同一コードが手書きで並んでおり、13要素以上の tuple では動かない。

これは設計として破綻しており、spec-emitter-guide §1.1 でも禁止された。

## 設計

### 原則

`in` 演算子は **iterable の汎用 `contains`** として処理する。コレクション型ごとの分岐は runtime が吸収し、emitter はコレクション型を意識しない。

### Rust での実現

| Python のコレクション | Rust の表現 | `in` の実現 |
|---|---|---|
| `list[T]` | `Vec<T>` / `PyList<T>` | `.contains(&key)` |
| `tuple[T, ...]` | `Vec<T>` に変換 or slice | `.contains(&key)` |
| `set[T]` | `HashSet<T>` / `PySet<T>` | `.contains(&key)` |
| `dict[K, V]` | `HashMap<K, V>` / `PyDict<K, V>` | `.contains_key(&key)` |
| `str` | `String` | `.contains(&substring)` |
| `range(n)` | 算術判定 | `start <= x && x < stop && (x - start) % step == 0` |

### tuple の扱い

tuple は固定長の異なる型を持てるが、`in` で使う場合は要素が同一型であることが前提（Python でも `1 in (1, "a", True)` は型混在だが、Pytra の型システムでは `tuple[int, int, int]` のように同一型が前提）。

Rust emitter が tuple の `in` を処理するとき:

1. EAST3 の `Tuple.elements` を `&[elem1, elem2, ...]` のスライスリテラルに変換
2. `.contains(&key)` を呼ぶ

```rust
// Python: x in (1, 2, 3)
// Rust:
[1, 2, 3].contains(&x)
```

これで要素数に関係なく動く。要素数ごとの trait impl は不要。

### range の扱い

`x in range(start, stop, step)` は配列を生成せず算術で判定:

```rust
// Python: x in range(0, 1000, 2)
// Rust:
x >= 0 && x < 1000 && (x - 0) % 2 == 0
```

ただし EAST3 で `range` は `RangeExpr` に正規化済みなので、emitter は `Compare(In) + RangeExpr` のパターンで直接算術判定を emit できる。

## 実施順序

1. Rust emitter の `_emit_compare` で `In` / `NotIn` + `Tuple` を `[...].contains(&key)` に変換する
2. Rust emitter の `_emit_compare` で `In` / `NotIn` + `RangeExpr` を算術判定に変換する
3. `PyContains` の tuple 要素数別 impl (2〜12要素) を `py_runtime.rs` から削除する
4. `in_membership_iterable` fixture が Rust で compile + run parity PASS することを確認する
5. fixture + sample の全件 parity に回帰がないことを確認する

## 関連

- P0-EAST3-IN-EXPAND: EAST3 optimizer による少数リテラルの `||` 展開（最適化）。本タスクとは独立で、両方実施してよい。optimizer 展開が先に適用された場合、emitter は `BoolOp(Or)` を描画するだけになり、本タスクの `contains` パスは通らない。optimizer が展開しなかったケース（4要素以上、非リテラル）では本タスクの `contains` パスが使われる。
