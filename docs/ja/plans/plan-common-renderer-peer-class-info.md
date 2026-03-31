# 計画: linker に receiver_storage_hint を追加 (P0-LINKER-RECEIVER-HINT)

## 背景

transpile された stdlib（例: `pytra.std.pathlib.Path`）を entry module から使うとき、emitter は receiver が ref class か value class かを知る必要がある。

- Rust: ref class なら `child.borrow().write_text(...)` が必要
- C++: ref class なら `child->write_text(...)` が必要
- Go: ref class ならポインタレシーバ

### linked EAST3 に既にある情報

| 情報 | フィールド | 状態 |
|---|---|---|
| property 判定 | `Attribute.attribute_access_kind: "property_getter"` | ✅ ある |
| method の戻り値型 | `Call.resolved_type` | ✅ ある |
| method 判定 | `Attribute.resolved_type: "callable"` | ✅ ある |
| receiver の class_storage_hint | なし | ❌ ない |

**足りないのは `class_storage_hint` だけ。**

## 設計

### linker が追加するフィールド

`Attribute` ノードと `Call` ノードの receiver が user-defined class 型のとき、linker が `receiver_storage_hint` フィールドを追加する:

```json
{
  "kind": "Attribute",
  "attr": "write_text",
  "value": {"kind": "Name", "id": "child", "resolved_type": "Path"},
  "resolved_type": "callable",
  "attribute_access_kind": "property_getter",
  "receiver_storage_hint": "ref"
}
```

値は `"ref"` または `"value"`。peer module の `ClassDef.class_storage_hint` からコピーするだけ。

### linker の実装箇所

linker は既に linked bundle の全 module EAST3 を持っている。class_name → class_storage_hint のマップを構築し、`Attribute` / `Call` ノードの receiver の `resolved_type` を引いて `receiver_storage_hint` を書き込む。

```
link 時:
1. 全 module の ClassDef を走査し、{class_name: class_storage_hint} を構築
2. 全 module の Attribute / Call ノードを走査
3. receiver の resolved_type が class_name に一致したら receiver_storage_hint を付与
```

### emitter 側の変更

emitter は `receiver_storage_hint` を見るだけ:

```python
# Rust emitter の _emit_attribute
hint = node.get("receiver_storage_hint", "value")
if hint == "ref":
    return f"{receiver}.borrow().{attr}"
else:
    return f"{receiver}.{attr}"
```

peer module を読む必要はない。CommonRenderer / PeerClassRegistry も不要。

## 影響範囲

- linker に class_storage_hint マップ構築 + ノード走査の pass を追加
- 全言語の linked EAST3 に `receiver_storage_hint` フィールドが増える
- emitter は任意でこのフィールドを参照（使わなくても壊れない）
- fixture + sample parity の全言語確認が必要

## 実施順序

1. linker に `receiver_storage_hint` 付与 pass を追加する
2. Rust emitter の `_emit_attribute` / `_emit_call` で `receiver_storage_hint` を参照する
3. `pathlib_extended` / `path_stringify` fixture が Rust で compile + run parity PASS することを確認する
4. fixture + sample の全件 parity に回帰がないことを確認する
