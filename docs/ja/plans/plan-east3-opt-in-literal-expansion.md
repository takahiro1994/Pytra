# 計画: EAST3 optimizer による `in` リテラル展開 (P0-EAST3-IN-EXPAND)

## 背景

Python の `x in (1, 2, 3)` や `x in [1, 2]` は iterable の `__contains__` として処理されるべきだが、要素が少数のリテラルの場合は `x == 1 || x == 2 || x == 3` に展開した方が実行時コスト（配列生成 + ループ）を避けられる。

この展開は **EAST3 optimizer** の責務であり、emitter が要素数を見て判断してはならない（spec-emitter-guide §1.1）。

## 設計

### 対象パターン

EAST3 の `Compare` ノードで:
- `ops` が `["In"]` または `["NotIn"]`
- `comparators[0]` が `Tuple` または `List`
- 全 `elements` が `Constant`（リテラル）
- 要素数が閾値 N 以下（N = 3 を推奨）

### 変換

**Before (EAST3 入力)**:

```json
{
  "kind": "Compare",
  "left": {"kind": "Name", "id": "x", "resolved_type": "int64"},
  "ops": ["In"],
  "comparators": [{
    "kind": "Tuple",
    "elements": [
      {"kind": "Constant", "value": 1, "resolved_type": "int64"},
      {"kind": "Constant", "value": 2, "resolved_type": "int64"}
    ]
  }]
}
```

**After (EAST3 optimizer 出力)**:

```json
{
  "kind": "BoolOp",
  "op": "Or",
  "values": [
    {
      "kind": "Compare",
      "left": {"kind": "Name", "id": "x", "resolved_type": "int64"},
      "ops": ["Eq"],
      "comparators": [{"kind": "Constant", "value": 1, "resolved_type": "int64"}]
    },
    {
      "kind": "Compare",
      "left": {"kind": "Name", "id": "x", "resolved_type": "int64"},
      "ops": ["Eq"],
      "comparators": [{"kind": "Constant", "value": 2, "resolved_type": "int64"}]
    }
  ],
  "resolved_type": "bool"
}
```

`NotIn` の場合は `BoolOp(And, [Compare(NotEq), ...])` に変換。

### 閾値

- N = 3 を推奨。4 以上は iterable の `contains` のまま残す
- 閾値は optimizer のパラメータとし、ハードコードしない

### 対象外

- 要素に非リテラル（変数、関数呼び出し等）を含む場合は展開しない — 副作用の評価順序が変わるリスク
- `x in range(...)` は別の最適化（range membership test）であり、本タスクの対象外
- `x in set_literal` は set の O(1) lookup が有利なので展開しない

## 実装箇所

`src/toolchain2/optimize/` 配下に pass を追加。既存の optimizer pass 列に組み込む。

## 影響範囲

- EAST3 のノード形状が変わるため、変換後の golden に差分が出る
- emitter は変換後の `BoolOp` / `Compare(Eq)` を描画するだけなので変更不要
- 全言語の fixture + sample parity で回帰がないことを確認する
