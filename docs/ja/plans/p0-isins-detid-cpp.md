# P0-ISINS-DETID-CPP: C++ emitter の PYTRA_TID_* 逆引きを削除し型名ベースに移行する

最終更新: 2026-04-03

## 背景

EAST3 の `IsInstance` ノードが `expected_type_id: {"id": "PYTRA_TID_DICT"}` のように廃止予定の type_id 定数を参照している（spec-adt.md §6 で廃止予定と明記済み）。

C++ emitter はこの `PYTRA_TID_*` を内部で型名に逆引きするテーブルを持っており、`PYTRA_TID_DICT` → `dict` → `std::holds_alternative<dict<...>>` のように変換している。

infra の P0-ISINSTANCE-DETID (S1-S3) で EAST3 の `IsInstance` ノードが `expected_type_name: "dict"` を直接持つように変更される。その後、C++ emitter の逆引きテーブルが不要になるので削除する。

## 前提条件

- infra の P0-ISINSTANCE-DETID S1-S3 が完了していること
- EAST3 golden に `PYTRA_TID_*` が出現しないこと

## 対象

- `src/toolchain2/emit/cpp/emitter.py` — `PYTRA_TID_*` → 型名の逆引きテーブルおよび関連ロジック

## 変更内容

現在の C++ emitter の isinstance 処理:

```python
# 現在: PYTRA_TID_* を型名に逆引き
expected_name = _normalize_expected_type_name(expected_type_id)  # "PYTRA_TID_DICT" → "dict"
```

変更後:

```python
# 変更後: expected_type_name を直接使用
expected_name = _str(node, "expected_type_name")  # "dict"
```

削除対象:
- `_normalize_expected_type_name` の `PYTRA_TID_*` 分岐
- `_TYPE_ID_TO_NAME` 等の逆引きテーブル（存在する場合）

## 受け入れ基準

- [ ] C++ emitter が `expected_type_name` を直接参照する
- [ ] `PYTRA_TID_*` の逆引きテーブルが C++ emitter から消えている
- [ ] isinstance を使う fixture（`isinstance_narrowing`, `isinstance_pod_exact`, `isinstance_tuple_check` 等）が C++ parity PASS
- [ ] fixture + sample + stdlib の C++ parity に回帰がない

## 決定ログ

- 2026-04-03: infra の P0-ISINSTANCE-DETID から C++ emitter 側の作業を分離して起票。infra が EAST3 を変更した後に着手する。
