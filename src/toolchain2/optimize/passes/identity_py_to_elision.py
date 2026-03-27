"""Elide statically-proven identity py_to/unbox casts in EAST3."""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result


_RUNTIME_CALL_TARGETS: dict[str, str] = {
    "py_to_bool": "bool",
    "py_to_float64": "float64",
    "py_to_int64": "int64",
    "py_to_string": "str",
}


def _canonical_type_name(value: JsonVal) -> str:
    type_name = ""
    if isinstance(value, str):
        type_name = value.strip()
    if type_name == "int":
        return "int64"
    if type_name == "float":
        return "float64"
    if type_name == "byte":
        return "uint8"
    return type_name


def _is_any_like_type(type_name: str) -> bool:
    t = type_name.strip()
    return t == "" or t == "unknown" or t == "Any" or t == "object" or t == "Obj"


def _types_match(lhs: JsonVal, rhs: JsonVal) -> bool:
    left_t = _canonical_type_name(lhs)
    right_t = _canonical_type_name(rhs)
    if left_t == "" or left_t == "unknown" or right_t == "" or right_t == "unknown":
        return False
    if _is_any_like_type(left_t) or _is_any_like_type(right_t):
        return False
    return left_t == right_t


class IdentityPyToElisionPass(East3OptimizerPass):
    """Drop no-op py_to-equivalent conversions when source type is already known."""

    name: str = "IdentityPyToElisionPass"
    min_opt_level: int = 1

    def _fold_call(self, node: dict[str, JsonVal]) -> JsonVal:
        if node.get("kind") != "Call":
            return None
        if node.get("lowered_kind") != "BuiltinCall":
            return None
        args_obj = node.get("args")
        args = args_obj if isinstance(args_obj, list) else []
        if len(args) != 1:
            return None
        arg0 = args[0]
        if not isinstance(arg0, dict):
            return None

        runtime_call = _canonical_type_name(node.get("runtime_call"))
        if runtime_call == "static_cast":
            target_t = _canonical_type_name(node.get("target"))
            if target_t == "" or target_t == "unknown":
                target_t = _canonical_type_name(node.get("resolved_type"))
        else:
            target_t = _RUNTIME_CALL_TARGETS.get(runtime_call, "")

        if target_t == "" or target_t == "unknown":
            return None
        if _types_match(arg0.get("resolved_type"), target_t):
            return arg0
        return None

    def _fold_unbox_like(self, node: dict[str, JsonVal]) -> JsonVal:
        kind = node.get("kind")
        if not isinstance(kind, str):
            return None
        if kind != "Unbox" and kind != "CastOrRaise":
            return None
        value_obj = node.get("value")
        value = value_obj if isinstance(value_obj, dict) else None
        if value is None:
            return None
        target_t = _canonical_type_name(node.get("target"))
        if target_t == "" or target_t == "unknown":
            target_t = _canonical_type_name(node.get("resolved_type"))
        if target_t == "" or target_t == "unknown":
            return None
        if _is_any_like_type(target_t):
            return None
        if _types_match(value.get("resolved_type"), target_t):
            return value
        return None

    def _rewrite(self, node: JsonVal) -> tuple[JsonVal, int]:
        if isinstance(node, list):
            list_out = node
            changed = 0
            for idx, item in enumerate(node):
                new_item, delta = self._rewrite(item)
                if new_item is not item:
                    list_out[idx] = new_item
                changed += delta
            return list_out, changed

        if not isinstance(node, dict):
            return node, 0

        dict_out = node
        changed = 0
        keys = list(node.keys())
        for key in keys:
            value = node.get(key)
            new_value, delta = self._rewrite(value)
            if new_value is not value:
                dict_out[key] = new_value
            changed += delta

        folded = self._fold_call(dict_out)
        if folded is not None:
            return folded, changed + 1
        folded = self._fold_unbox_like(dict_out)
        if folded is not None:
            return folded, changed + 1
        return dict_out, changed

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        _ = context
        _, change_count = self._rewrite(east3_doc)
        warnings: list[str] = []
        return make_pass_result(change_count > 0, change_count, warnings, 0.0)
