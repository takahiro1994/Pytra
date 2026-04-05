"""Expand small literal `in`/`not in` compares into BoolOp chains."""

from __future__ import annotations

from typing import Any

from toolchain.compile.east3_optimizer import East3OptimizerPass
from toolchain.compile.east3_optimizer import PassContext
from toolchain.compile.east3_optimizer import PassResult


_MAX_LITERAL_EXPANSION = 3


def _deep_copy_json(val: Any) -> Any:
    if val is None or isinstance(val, bool) or isinstance(val, int) or isinstance(val, float) or isinstance(val, str):
        return val
    if isinstance(val, list):
        return [_deep_copy_json(item) for item in val]
    if isinstance(val, dict):
        out: dict[str, Any] = {}
        for key in val:
            out[key] = _deep_copy_json(val[key])
        return out
    return val


def _clone_expr(expr: Any) -> dict[str, Any] | None:
    if not isinstance(expr, dict):
        return None
    cloned = _deep_copy_json(expr)
    return cloned if isinstance(cloned, dict) else None


def _is_literal_seq(expr: Any) -> bool:
    if not isinstance(expr, dict):
        return False
    kind = expr.get("kind")
    if kind != "Tuple" and kind != "List":
        return False
    elements = expr.get("elements")
    if not isinstance(elements, list) or len(elements) == 0 or len(elements) > _MAX_LITERAL_EXPANSION:
        return False
    for elem in elements:
        if not isinstance(elem, dict) or elem.get("kind") != "Constant":
            return False
    return True


def _compare_node(op: str, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
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

    name = "InLiteralExpansionPass"
    min_opt_level = 1

    def _fold_compare(self, node: dict[str, Any]) -> dict[str, Any] | None:
        if node.get("kind") != "Compare":
            return None
        ops = node.get("ops")
        comparators = node.get("comparators")
        if not isinstance(ops, list) or not isinstance(comparators, list):
            return None
        if len(ops) != 1 or len(comparators) != 1:
            return None
        op = ops[0] if isinstance(ops[0], str) else ""
        if op != "In" and op != "NotIn":
            return None
        comparator = comparators[0]
        if not _is_literal_seq(comparator):
            return None
        left = node.get("left")
        if not isinstance(left, dict):
            return None
        elements = comparator.get("elements")
        if not isinstance(elements, list):
            return None
        values: list[dict[str, Any]] = []
        cmp_op = "Eq" if op == "In" else "NotEq"
        for elem in elements:
            left_clone = _clone_expr(left)
            right_clone = _clone_expr(elem)
            if left_clone is None or right_clone is None:
                return None
            values.append(_compare_node(cmp_op, left_clone, right_clone))
        return {
            "kind": "BoolOp",
            "op": "Or" if op == "In" else "And",
            "values": values,
            "resolved_type": "bool",
            "borrow_kind": "value",
            "casts": [],
        }

    def _rewrite(self, node: Any) -> tuple[Any, int]:
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

    def run(self, east3_doc: dict[str, Any], context: PassContext) -> PassResult:
        _ = context
        _, change_count = self._rewrite(east3_doc)
        return PassResult(changed=change_count > 0, change_count=change_count)
