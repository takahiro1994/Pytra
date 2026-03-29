<a href="../../en/plans/p2-sample-benchmark.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P2-SAMPLE-BENCHMARK: sample parity check で実行時間を自動計測し README に反映する

最終更新: 2026-03-30
ステータス: 未着手

## 背景

`sample/README-ja.md` と `sample/README.md` に「実行速度の比較」テーブルがあるが、現在は手動計測で更新されている（最終計測: 2026-02-27）。parity check は sample を Python と各ターゲット言語で実行するため、そこで実行時間を自動計測すれば README の表を自動更新できる。

このマシンはハイスペック many-core なので 1 スレッド計測の安定性は十分。

## 設計

### 1. 実行時間の記録

parity check（fast 版）の sample 実行時に、Python と各ターゲットの実行時間を計測する。

記録先: `.parity-results/<target>_sample.json` の各ケースに `elapsed_sec` フィールドを追加。Python の計測結果は `.parity-results/python_sample.json` に記録する。

```json
{
  "target": "go",
  "case_root": "sample",
  "results": {
    "01_mandelbrot": {
      "category": "ok",
      "timestamp": "2026-03-30T12:00:00",
      "elapsed_sec": 0.753
    }
  }
}
```

### 2. 計測プロトコル

既存の計測条件に合わせるか、新プロトコルを定義する。

既存条件（`sample/README-ja.md` 記載）:
- warmup=1, repeat=5, `elapsed_sec` の中央値採用
- コンパイル時間は除外

parity check は現在 1 回実行のみなので、repeat を入れるとかなり遅くなる。選択肢:

1. **1 回実行の実測値をそのまま記録** — 速いが値がブレる可能性
2. **warmup=1, repeat=3 の中央値** — 既存より軽量だが安定
3. **`--benchmark` フラグで repeat モードを有効化** — 通常 parity は 1 回、ベンチマーク時だけ repeat

3 が最も柔軟。通常の parity check は速く、ベンチマーク更新したいときだけ `--benchmark` を付ける。

### 3. README テーブル自動生成

`tools/gen/gen_sample_benchmark.py` が `.parity-results/*_sample.json` を読み、`sample/README-ja.md` と `sample/README.md` の「実行速度の比較」テーブルを書き換える。

- テーブル部分だけを置換し、他のセクションはそのまま維持する
- 計測されていない言語/ケースは `—` 表示
- 計測日時をテーブル下部に記載
- 日英同時更新（テーブル内容は数字なので同一、見出しだけ言語切り替え）

### 4. 自動再生成

parity check の末尾で、`sample/README-ja.md` の mtime が 10 分以上古ければ `gen_sample_benchmark.py` を自動実行する。進捗マトリクスと同じ仕組み。

## 決定ログ

- 2026-03-30: parity check の sample 実行時に実行時間を計測し、README に自動反映する方針に決定。マシンが many-core でハイスペックなため、1 スレッド計測の安定性は十分と判断。
