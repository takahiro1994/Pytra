# P0: tagged union を object + type_id に統一

最終更新: 2026-03-20

関連 TODO:
- `docs/ja/todo/index.md` の `ID: P0-TAGGED-UNION-OBJECT-BOX-01`

## 背景

現在 tagged union（`str | Path` 等）は型ごとに専用 struct を生成している:

```cpp
struct _Union_str_Path {
    pytra_type_id tag;
    str str_val;
    Path path_val;  // ← Path の完全定義が必要
};
```

これにより:
1. **前方参照問題**: `_Union_str_Path` が `Path` より先に定義される必要があるが、`Path` のコンストラクタが `_Union_str_Path` を引数に取る。相互依存で解決不能。
2. **全バックエンド共通**: 値型セマンティクスの言語（C++, Rust, Go, Swift）全てで発生。
3. **struct 肥大化**: メンバ数分のフィールドを持つ。

## 設計

### 新しい tagged union 表現

```cpp
// 全 tagged union 共通。型ごとの struct 生成は不要。
// value は rc<RcObject> (= object) で、unbox して使う。
```

- **tag**: `pytra_type_id` — メンバの型を識別
- **value**: `object` (= `rc<RcObject>`) — ボックス化された値

### unbox 制約

- tagged union の値は必ず `isinstance` で型を確認した後に **unbox してから使う**。
- `object` のまま演算（`+`, `.method()` 等）を呼ぶことは禁止。
- emitter は `isinstance` 分岐で narrow された型で emit する。narrow 前の `object` のまま演算する emit は生成しない。
- EAST3 の型推論が narrow を追跡しているので、emitter 側の変更は最小限。

### POD union の扱い

`int | float` のような POD 同士の union でもヒープ確保が入る。
まずは全部 `object + tag` で統一し、POD 最適化は後続タスクで検討。

### 各バックエンドの表現

| バックエンド | 表現 |
|-------------|------|
| C++ | `object` (= `rc<RcObject>`) + `pytra_type_id` |
| Rust | `Box<dyn Any>` + type_id、または enum のまま（Box 化） |
| Go | `interface{}` + type assertion |
| Java/C#/Kotlin | `Object` + `instanceof`（既に参照型） |
| Swift | `indirect enum` |
| JS/TS | そのまま（動的型付き） |

### 削除対象

- `_Union_*` struct の自動生成ロジック（`cpp_emitter.py` の `_inline_union_structs` 等）
- tagged union 用の型ごと struct 定義

## 対象ファイル

| ファイル | 変更 |
|---------|------|
| `src/backends/cpp/emitter/cpp_emitter.py` | `_Union_*` struct 生成を `object + tag` に変更 |
| `src/backends/cpp/emitter/type_bridge.py` | tagged union 型の C++ 表現を変更 |
| `src/backends/cpp/emitter/header_builder.py` | union struct 生成除去 |
| `src/toolchain/ir/` | EAST3 レベルでの tagged union 表現検討 |
| 各バックエンド emitter | 同様の変更 |

## 受け入れ基準

- [ ] tagged union が `object + type_id` で表現される（型ごとの struct 不要）。
- [ ] `str | Path` のような自己参照 union が前方参照問題なしにコンパイルできる。
- [ ] unbox 制約: `object` のまま演算を emit しない。
- [ ] `pathlib.py` の `out/cpp/` g++ ビルドが通る。
- [ ] `check_py2x_transpile --target cpp` pass。

## 子タスク

- [ ] [ID: P0-TAGGED-UNION-OBJECT-BOX-01-S1] C++ emitter の tagged union 生成を `object + type_id` 方式に変更する。`_Union_*` struct 生成を除去。
- [ ] [ID: P0-TAGGED-UNION-OBJECT-BOX-01-S2] unbox 時の `isinstance` → `static_cast` emit を実装する。
- [ ] [ID: P0-TAGGED-UNION-OBJECT-BOX-01-S3] `pathlib.py` を含む `out/cpp/` g++ ビルドを検証する。
- [ ] [ID: P0-TAGGED-UNION-OBJECT-BOX-01-S4] 他バックエンド（Rust, Go 等）への展開を検討する。

## 決定ログ

- 2026-03-20: `pathlib.h` の g++ ビルドで `_Union_str_Path` ↔ `Path` の相互依存が発覚。tagged union struct のフィールドが incomplete type を持てない問題。
- 2026-03-20: 全バックエンド共通の問題であることを確認。値型セマンティクスの言語全てで発生。
- 2026-03-20: ユーザー提案: tagged union は `object` (rc) + `type_id` だけ持ち、unbox して使う。POD 以外をボックス化するより、全部 object + tag で統一する方がシンプル。unbox してしか使わない制約を入れる。
