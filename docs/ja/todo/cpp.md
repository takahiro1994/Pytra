<a href="../../en/todo/cpp.md">
  <img alt="Read in English" src="https://img.shields.io/badge/docs-English-2563EB?style=flat-square">
</a>

# TODO — C++ backend

> 領域別 TODO。全体索引は [index.md](./index.md) を参照。

最終更新: 2026-03-31

## 運用ルール

- 各タスクは `ID` と文脈ファイル（`docs/ja/plans/*.md`）を必須にする。
- 優先度順（小さい P 番号から）に着手する。
- 進捗メモとコミットメッセージは同一 `ID` を必ず含める。
- **タスク完了時は `[ ]` を `[x]` に変更し、完了メモを追記してコミットすること。**
- 完了済みタスクは定期的に `docs/ja/todo/archive/` へ移動する。
- **parity テストは「emit + compile + run + stdout 一致」を完了条件とする。**
- **[emitter 実装ガイドライン](../spec/spec-emitter-guide.md)を必ず読むこと。** parity check ツール、禁止事項、mapping.json の使い方が書いてある。

## 未完了タスク

### P0-CPP-VARIANT: C++ を std::variant ベースに移行し object/box/unbox を廃止する

文脈: [docs/ja/plans/plan-cpp-variant-migration.md](../plans/plan-cpp-variant-migration.md)

union type を `object` に退化させず `std::variant` で表現する。`work/tmp/variant_test.cpp` で基本動作・再帰型・RC共有・callable を実証済み。C++ で先に実証し、成功したら EAST の object 退化を廃止する。

**Phase 1: variant 出力追加**

1. [ ] [ID: P0-CPP-VARIANT-S1] C++ emitter に `UnionType` → `std::variant<T1, T2, ...>` の型変換パスを追加する
2. [ ] [ID: P0-CPP-VARIANT-S2] isinstance narrowing を `std::holds_alternative<T>` + `std::get<T>` に変換する
3. [ ] [ID: P0-CPP-VARIANT-S3] 再帰型を `struct { variant<..., shared_ptr<vector<Self>>> }` で出力する
4. [ ] [ID: P0-CPP-VARIANT-S4] 基本 union fixture（`int | str`, `str | None` 等）が C++ で PASS することを確認する

**Phase 2: object 型を削除**

5. [ ] [ID: P0-CPP-VARIANT-S5] C++ emitter の `object` 型出力を全て `std::variant` に置換する
6. [ ] [ID: P0-CPP-VARIANT-S6] `PYTRA_TID_*` / `py_runtime_object_type_id` / `object.h` の `object` クラスを削除する
7. [ ] [ID: P0-CPP-VARIANT-S7] fixture 全件 + sample 全件が `object` 型なしで PASS することを確認する

**Phase 3: box/unbox 削除**

8. [ ] [ID: P0-CPP-VARIANT-S8] C++ emitter の box/unbox 処理を削除し、variant 代入 / `std::get` に置換する
9. [ ] [ID: P0-CPP-VARIANT-S9] `yields_dynamic` 依存コードを C++ emitter から削除する

**Phase 4: EAST から object 退化 / box / unbox を削除**

10. [ ] [ID: P0-CPP-VARIANT-S10] lower.py の Boxing（`resolved_type="object"` 生成）と iter boundary を削除する
11. [ ] [ID: P0-CPP-VARIANT-S11] EAST3 validation に「`resolved_type: "object"` ならエラー」を追加する
12. [ ] [ID: P0-CPP-VARIANT-S12] 全言語の fixture + sample が PASS することを確認する

### P0-CPP-OBJECT-CONTAINER: object_container_access fixture の C++ parity を通す

文脈: [docs/ja/plans/plan-object-container-access-parity.md](../plans/plan-object-container-access-parity.md)

selfhost で必要な動的型パターン（`dict[str, object]` の items() unpack / get()、`list[object]` の index、str 不要 unbox、`set[tuple[str,str]]`）を網羅する fixture。EAST3 には全て情報が載っている。selfhost build (S5) の前提。

1. [ ] [ID: P0-CPP-OBJ-CONT-S1] `object_container_access` fixture が C++ で compile + run parity PASS することを確認する（失敗なら emitter を修正）

### P20-CPP-SELFHOST: C++ emitter で toolchain2 を C++ に変換し g++ build を通す

文脈: [docs/ja/plans/p4-cpp-selfhost.md](../plans/p4-cpp-selfhost.md)

1. [x] [ID: P20-CPP-SELFHOST-S0] selfhost 対象コード（`src/toolchain2/` 全 .py）で戻り値型の注釈が欠けている関数に型注釈を追加する — resolve が `inference_failure` にならない状態にする（他言語と共通。先に完了した側の成果を共有）
   - 完了: `ast` 走査で `src/toolchain2/` 全 `.py` の `FunctionDef` / `AsyncFunctionDef` を監査し、戻り値注釈欠落が 0 件であることを確認。回帰防止として `tools/unittest/selfhost/test_selfhost_return_annotations.py` を追加した
2. [x] [ID: P20-CPP-SELFHOST-S1] toolchain2 全 .py を C++ に emit し、g++ build が通ることを確認する
   - 完了: code_emitter.py → code_emitter.cpp 生成・リンク成功（runtime cpp + 依存 .cpp と結合）
3. [x] [ID: P20-CPP-SELFHOST-S2] g++ build 失敗ケースを emitter/runtime の修正で解消する（EAST の workaround 禁止）
   - 完了: tuple subscript 検出拡張、py_dict_set_mut 追加、object→str/container 型強制、前方宣言二段階出力、is_simple_ident ガード、py_set_add_mut fallback を py_to_string 経由に変更
4. [x] [ID: P20-CPP-SELFHOST-S3] selfhost 用 C++ golden を配置し、回帰テストとして維持する
   - 完了: `python3 tools/gen/regenerate_selfhost_golden.py --target cpp --timeout 60` で `test/selfhost/cpp/` の golden を再生成し、emit 成功する 42 モジュールを更新した。emit 失敗する 5 モジュール（`toolchain2.compile.passes`, `toolchain2.optimize.passes.{tuple_target_direct_expansion,typed_enumerate_normalization,typed_repeat_materialization}`, `toolchain2.resolve.py.resolver`）は既知 skip として整理し、`tools/unittest/selfhost/test_selfhost_cpp_golden.py` に C++ 専用の golden coverage / re-emit 一致テストを追加した
5. [x] [ID: P20-CPP-SELFHOST-S4] emit 失敗の 5 モジュールを解消し、toolchain2 全モジュールの C++ emit を成功させる
   - 完了: `tools/gen/regenerate_selfhost_golden.py` の `collect_east3_opt_entries()` が 47 モジュールを返し、従来 skip していた `toolchain2.compile.passes`, `toolchain2.resolve.py.resolver`, `toolchain2.optimize.passes.{tuple_target_direct_expansion,typed_enumerate_normalization,typed_repeat_materialization}` も対象に入る状態まで C++ emit failure を解消した。selfhost C++ golden の現状差分は emit failure ではなく golden mismatch のみ。
6. [ ] [ID: P20-CPP-SELFHOST-S5] selfhost C++ バイナリを g++ でビルドし、リンクが通ることを確認する
7. [ ] [ID: P20-CPP-SELFHOST-S6] `run_selfhost_parity.py --selfhost-lang cpp --emit-target cpp --case-root fixture` で fixture parity が PASS することを確認する
8. [ ] [ID: P20-CPP-SELFHOST-S7] `run_selfhost_parity.py --selfhost-lang cpp --emit-target cpp --case-root sample` で sample parity が PASS することを確認する
