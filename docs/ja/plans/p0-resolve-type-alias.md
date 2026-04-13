# P0-RESOLVE-TYPE-ALIAS: 型エイリアスの同値性判定を正しく実装する

最終更新: 2026-04-13

## 背景

C++ selfhost build で `list[Node]` に `dict[str, JsonVal]` を append するとき、emitter が型不一致と判定して covariant copy を生成する。`Node = dict[str, JsonVal]` は型エイリアスであり、両者は同一型。

## 問題

`normalize_type()` が型エイリアス展開と構文正規化（`List` → `list`, `Optional` → `| None`）を 1 つの関数で担当している。再帰型エイリアス（`JsonVal`）を展開すると無限再帰を回避するため `Any` に退化する。

結果:
- `Node` → `dict[str, JsonVal]`（1 段展開、OK）
- `dict[str, JsonVal]` の `JsonVal` を展開しようとすると → 再帰 → `Any` に退化
- `list[Node]` の展開結果と `list[dict[str, JsonVal]]` の展開結果が一致する保証がない

## 方針

### 型エイリアス展開の一貫したルール

| 種別 | 定義例 | 展開動作 |
|------|--------|----------|
| 非再帰エイリアス | `Node = dict[str, JsonVal]` | **完全展開**。`Node` → `dict[str, JsonVal]` |
| 自己再帰エイリアス | `type JsonVal = None \| bool \| ... \| list[JsonVal]` | **名前保持**。`JsonVal` → `JsonVal` のまま |
| 相互再帰エイリアス | `type A = list[B]`, `type B = dict[str, A]` | **禁止**。parse 時にエラー |

### なぜ一意になるか

1. 非再帰エイリアスは完全展開するので、元の名前に依存しない正規形になる
2. 自己再帰エイリアスは名前を保持するので、同じ名前なら同一型
3. 相互再帰を禁止することで、「A を先に展開するか B を先に展開するか」で結果が変わる曖昧さを排除

### 判定方法

「自己再帰か否か」は、展開中に自分の名前が出現するかで機械的に判定できる（現在の `_seen` ガードと同じ原理）。ただし、`Any` に退化させるのではなく、名前をそのまま返す。

## 修正対象

### `normalize_type()` の変更

```python
# 現状（再帰ガードで Any に退化）
if t in seen:
    return "Any"

# 修正後（再帰ガードで名前を保持）
if t in seen:
    return t
```

### 相互再帰の検出

parse の TypeAlias pre-scan（`resolver.py:4782-4797`）で、エイリアス間の依存グラフを構築し、長さ 2 以上のサイクルがあればエラーにする。長さ 1 のサイクル（自己再帰）は許可。

## 影響

- **全言語に影響する resolve 修正**。EAST3 の resolved_type が変わる可能性があるため golden 再生成が必要
- `JsonVal` が `Any` に退化していた箇所が `JsonVal` のまま保持されるようになるため、emitter の型マッピングに `JsonVal` エントリが必要になる可能性がある
- fixture parity への影響は小さいはず（fixture では再帰型エイリアスをほぼ使っていない）

## spec への追記

`spec-east.md` に以下を追記する:

- 型エイリアスは resolve が正規形に展開した状態で EAST3 に書き込む
- 非再帰エイリアスは完全展開、自己再帰エイリアスは名前保持
- 相互再帰型エイリアスは禁止（parse エラー）
