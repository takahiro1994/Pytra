<a href="../../en/plans/p7-go-selfhost-runtime.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# P7-GO-SELFHOST-RUNTIME: Go selfhost バイナリを実際に動かして parity PASS する

最終更新: 2026-03-31
ステータス: 未着手

## 背景

P6-GO-SELFHOST で `go build` は通ったが、selfhost バイナリが実際に fixture/sample/stdlib を変換して正しい出力を生成するにはまだギャップがある。`run_selfhost_parity.py --selfhost-lang go` で parity PASS するのが最終目標。

## 問題点（Go 担当の分析）

### 1. linker の type_id 割り当て失敗

`CommonRenderer(ABC)` 等、外部ベースクラスを持つ class の階層が type_id 解決できない。外部クラスは `object` にフォールバックすべき。

### 2. Go emitter 自身の Go 翻訳が golden にない

`test/selfhost/go/` は `emit/go/` を意図的に除外している（循環依存回避）。しかし selfhost バイナリに `emit_go_module` の Go 翻訳が含まれないと、Go selfhost コンパイラが Go コードを emit できない。

循環依存の回避策:
- Go emitter の Go 翻訳を別パッケージとして分離し、selfhost ビルド時にリンクする
- または `emit/go/` の翻訳を golden に含め、ビルド時に全ファイルを結合する

### 3. main() が空

Go 翻訳された `main()` は Python の `pytra-cli2` の CLI ロジックを持たない。EAST3 JSON を読んで emit する最小の CLI wrapper が必要。

```go
// main.go (最小 CLI wrapper)
func main() {
    input := os.Args[1]
    east3 := loadEAST3(input)
    code := emit_go_module(east3)
    fmt.Print(code)
}
```

## フロー

1. linker 修正 — 外部クラスの type_id フォールバック
2. Go emitter の Go 翻訳を selfhost に含める
3. CLI wrapper 追加
4. `run_selfhost_parity.py --selfhost-lang go` で検証

## 検証方法

```bash
python3 tools/run/run_selfhost_parity.py --selfhost-lang go
```

PASS 条件: fixture + sample + stdlib の全件で、selfhost Go バイナリが emit したコードの実行結果が Python と一致する。

## 決定ログ

- 2026-03-31: P6 完了後の分析で3つのギャップが判明。Go 担当が対処する方針に決定。
