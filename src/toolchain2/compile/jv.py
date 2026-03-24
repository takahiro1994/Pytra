"""JsonVal helpers for EAST2 → EAST3 lowering.

Provides typed access to JSON trees without using Any/object.
§5.1: Any/object 禁止。
§5.3: Python 標準モジュール直接 import 禁止。
"""

from __future__ import annotations

from typing import Union


# JsonVal 再帰型エイリアス (pytra.std.json.JsonVal と同等)
JsonVal = Union[None, bool, int, float, str, list["JsonVal"], dict[str, "JsonVal"]]

# Node = dict[str, JsonVal]
Node = dict[str, JsonVal]


def jv_str(v: JsonVal) -> str:
    """JsonVal が str なら返す。それ以外は空文字。"""
    if isinstance(v, str):
        return v
    return ""


def jv_str_or(v: JsonVal, default: str) -> str:
    if isinstance(v, str):
        return v
    return default


def jv_int(v: JsonVal) -> int:
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    return 0


def jv_bool(v: JsonVal) -> bool:
    if isinstance(v, bool):
        return v
    return False


def jv_list(v: JsonVal) -> list[JsonVal]:
    if isinstance(v, list):
        return v
    return []


def jv_dict(v: JsonVal) -> Node:
    if isinstance(v, dict):
        return v
    return {}


def jv_is_dict(v: JsonVal) -> bool:
    return isinstance(v, dict)


def jv_is_list(v: JsonVal) -> bool:
    return isinstance(v, list)


def nd_kind(node: Node) -> str:
    return jv_str(node.get("kind", ""))


def nd_get_str(node: Node, key: str) -> str:
    return jv_str(node.get(key, ""))


def nd_get_str_or(node: Node, key: str, default: str) -> str:
    return jv_str_or(node.get(key), default)


def nd_get_dict(node: Node, key: str) -> Node:
    return jv_dict(node.get(key))


def nd_get_list(node: Node, key: str) -> list[JsonVal]:
    return jv_list(node.get(key))


def nd_get_int(node: Node, key: str) -> int:
    return jv_int(node.get(key))


def nd_get_bool(node: Node, key: str) -> bool:
    return jv_bool(node.get(key))


def nd_source_span(node: Node) -> JsonVal:
    return node.get("source_span")


def nd_repr(node: Node) -> str:
    return jv_str(node.get("repr", ""))


def normalize_type_name(value: JsonVal) -> str:
    if isinstance(value, str):
        t = value.strip()
        if t != "":
            return t
    return "unknown"
