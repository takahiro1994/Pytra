"""Expand small literal `in`/`not in` compares into BoolOp chains."""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result


_MAX_LITERAL_EXPANSION = 3


def _deep_copy_json(val: JsonVal) -> JsonVal:
    if val is None or isinstance(val, bool) or isinstance(val, int) or isinstance(val, float) or isinstance(val, str):
        return val
    if isinstance(val, list):
        return [_deep_copy_json(item) for item in val]
    if isinstance(val, dict):
        out: dict[str, JsonVal] = {}
        for key in val:
            out[key] = _deep_copy_json(val[key])
        return out
    return val


def _clone_expr(expr: JsonVal) -> dict[str, JsonVal] | None:
    if not isinstance(expr, dict):
        return None
    cloned = _deep_copy_json(expr)
    return cloned if isinstance(cloned, dict) else None


def _is_literal_seq(expr: JsonVal) -> bool:
    if not isinstance(expr, dict):
        return False
    kind = expr.get("kind")
    if kind != "Tuple" and kind != "List":
        return False
    elements_obj = expr.get("elements")
    elements = elements_obj if isinstance(elements_obj, list) else []
    if len(elements) == 0 or len(elements) > _MAX_LITERAL_EXPANSION:
        return False
    for elem in elements:
        if not isinstance(elem, dict) or elem.get("kind") != "Constant":
            return False
    return True


def _compare_node(op: str, left: dict[str, JsonVal], right: dict[str, JsonVal]) -> dict[str, JsonVal]:
    return {
        "kind": "Compare",
        "left": left,
        "ops": [op],
        "comparators": [right],
        "resolved_type": "bool",
        "borrow_kind": "value",
        "casts": [],
    }


class InLiteralExpansionPass(East3OptimizerPass):
    """Rewrite small literal membership tests into Eq/NotEq chains."""

    name: str = "InLiteralExpansionPass"
    min_opt_level: int = 1

    def _fold_compare(self, node: dict[str, JsonVal]) -> JsonVal:
        if node.get("kind") != "Compare":
            return None
        ops_obj = node.get("ops")
        comparators_obj = node.get("comparators")
        ops = ops_obj if isinstance(ops_obj, list) else []
        comparators = comparators_obj if isinstance(comparators_obj, list) else []
        if len(ops) != 1 or len(comparators) != 1:
            return None
        op = ops[0] if isinstance(ops[0], str) else ""
        if op != "In" and op != "NotIn":
            return None
        comparator = comparators[0]
        if not _is_literal_seq(comparator):
            return None
        left_obj = node.get("left")
        left = left_obj if isinstance(left_obj, dict) else None
        if left is None:
            return None
        elements_obj = comparator.get("elements") if isinstance(comparator, dict) else None
        elements = elements_obj if isinstance(elements_obj, list) else []
        bool_values: list[JsonVal] = []
        cmp_op = "Eq" if op == "In" else "NotEq"
        for elem in elements:
            elem_node = elem if isinstance(elem, dict) else None
            left_clone = _clone_expr(left)
            right_clone = _clone_expr(elem_node)
            if left_clone is None or right_clone is None:
                return None
            bool_values.append(_compare_node(cmp_op, left_clone, right_clone))
        bool_op = "Or" if op == "In" else "And"
        return {
            "kind": "BoolOp",
            "op": bool_op,
            "values": bool_values,
            "resolved_type": "bool",
            "borrow_kind": "value",
            "casts": [],
        }

    def _rewrite(self, node: JsonVal) -> tuple[JsonVal, int]:
        if isinstance(node, list):
            changed = 0
            for idx, item in enumerate(node):
                new_item, delta = self._rewrite(item)
                if new_item is not item:
                    node[idx] = new_item
                changed += delta
            return node, changed
        if not isinstance(node, dict):
            return node, 0

        changed = 0
        for key, value in list(node.items()):
            new_value, delta = self._rewrite(value)
            if new_value is not value:
                node[key] = new_value
            changed += delta

        folded = self._fold_compare(node)
        if isinstance(folded, dict):
            return folded, changed + 1
        return node, changed

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        _ = context
        _, change_count = self._rewrite(east3_doc)
        return make_pass_result(changed=change_count > 0, change_count=change_count)
