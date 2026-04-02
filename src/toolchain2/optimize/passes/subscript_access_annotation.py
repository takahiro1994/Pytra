"""Annotate subscript access metadata for negative-index and bounds-check fastpaths."""

from __future__ import annotations

from pytra.std.json import JsonVal

from toolchain2.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result


def _stripped(value: JsonVal) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _is_non_negative_int_constant(expr: JsonVal) -> bool:
    if not isinstance(expr, dict):
        return False
    if expr.get("kind") != "Constant":
        return False
    value = expr.get("value")
    return isinstance(value, int) and not isinstance(value, bool) and int(value) >= 0


def _is_negative_int_literal(expr: JsonVal) -> bool:
    if not isinstance(expr, dict):
        return False
    if expr.get("kind") == "Constant":
        value = expr.get("value")
        return isinstance(value, int) and not isinstance(value, bool) and int(value) < 0
    if expr.get("kind") != "UnaryOp":
        return False
    if _stripped(expr.get("op")) not in ("USub", "Minus"):
        return False
    operand = expr.get("operand")
    if not isinstance(operand, dict) or operand.get("kind") != "Constant":
        return False
    value = operand.get("value")
    return isinstance(value, int) and not isinstance(value, bool)


def _is_range_runtime_call(expr: JsonVal) -> bool:
    if not isinstance(expr, dict) or expr.get("kind") != "Call":
        return False
    if _stripped(expr.get("runtime_call")) == "py_range":
        return True
    if _stripped(expr.get("lowered_kind")) != "BuiltinCall":
        return False
    return _stripped(expr.get("builtin_name")) == "range"


def _name_target_ids(target_plan: JsonVal) -> list[str]:
    if not isinstance(target_plan, dict):
        return []
    kind = _stripped(target_plan.get("kind"))
    if kind == "NameTarget":
        target_id = target_plan.get("id")
        if isinstance(target_id, str) and target_id != "":
            return [target_id]
        return []
    if kind == "TupleTarget":
        elements = target_plan.get("elements")
        if not isinstance(elements, list):
            return []
        out: list[str] = []
        for item in elements:
            for target_id in _name_target_ids(item):
                out.append(target_id)
        return out
    return []


def _is_range_for_plan(stmt: dict[str, JsonVal]) -> bool:
    if _stripped(stmt.get("kind")) != "ForCore":
        return False
    iter_plan = stmt.get("iter_plan")
    if not isinstance(iter_plan, dict):
        return False
    plan_kind = _stripped(iter_plan.get("kind"))
    if plan_kind == "StaticRangeForPlan":
        return True
    if plan_kind != "RuntimeIterForPlan":
        return False
    return _is_range_runtime_call(iter_plan.get("iter_expr"))


def _subscript_owner_type(node: dict[str, JsonVal]) -> str:
    owner = node.get("value")
    if not isinstance(owner, dict):
        return ""
    return _stripped(owner.get("resolved_type"))


def _supports_fast_index(node: dict[str, JsonVal]) -> bool:
    owner_type = _subscript_owner_type(node)
    if owner_type.startswith("list[") and owner_type.endswith("]"):
        return True
    return owner_type in ("str", "bytes", "bytearray")


class SubscriptAccessAnnotationPass(East3OptimizerPass):
    """Annotate Subscript nodes with subscript_access_v1 metadata."""

    name: str = "SubscriptAccessAnnotationPass"
    min_opt_level: int = 1

    def _default_negative_index(self, context: PassContext) -> str:
        raw = _stripped(context.debug_flags.get("negative_index_mode"))
        if raw == "always":
            return "normalize"
        return "skip"

    def _default_bounds_check(self, context: PassContext) -> str:
        raw = _stripped(context.debug_flags.get("bounds_check_mode"))
        if raw in ("always", "debug"):
            return "full"
        return "off"

    def _annotation_for_subscript(
        self,
        node: dict[str, JsonVal],
        context: PassContext,
        fast_index_names: set[str],
    ) -> dict[str, JsonVal] | None:
        if _stripped(node.get("kind")) != "Subscript":
            return None
        if not _supports_fast_index(node):
            return None
        slice_node = node.get("slice")
        negative_index = self._default_negative_index(context)
        bounds_check = self._default_bounds_check(context)
        reason = "optimizer_default"

        if isinstance(slice_node, dict):
            if _is_non_negative_int_constant(slice_node):
                negative_index = "skip"
                reason = "non_negative_constant"
            elif _is_negative_int_literal(slice_node):
                negative_index = "normalize"
                reason = "negative_literal"
            elif _stripped(slice_node.get("kind")) == "Name":
                name_id = slice_node.get("id")
                if isinstance(name_id, str) and name_id in fast_index_names:
                    negative_index = "skip"
                    bounds_check = "off"
                    reason = "for_range_index"

        return {
            "schema_version": "subscript_access_v1",
            "negative_index": negative_index,
            "bounds_check": bounds_check,
            "reason": reason,
        }

    def _annotate_meta(
        self,
        node: dict[str, JsonVal],
        context: PassContext,
        fast_index_names: set[str],
    ) -> int:
        annotation = self._annotation_for_subscript(node, context, fast_index_names)
        if annotation is None:
            return 0
        meta_obj = node.get("meta")
        meta = dict(meta_obj) if isinstance(meta_obj, dict) else {}
        current = meta.get("subscript_access_v1")
        if current == annotation:
            return 0
        meta["subscript_access_v1"] = annotation
        node["meta"] = meta
        return 1

    def _visit(
        self,
        node: JsonVal,
        context: PassContext,
        fast_index_names: set[str],
    ) -> int:
        changed = 0
        if isinstance(node, list):
            for item in node:
                changed += self._visit(item, context, fast_index_names)
            return changed
        if not isinstance(node, dict):
            return 0

        changed += self._annotate_meta(node, context, fast_index_names)

        nested_fast_index_names = fast_index_names
        if _is_range_for_plan(node):
            nested_fast_index_names = set(fast_index_names)
            for target_id in _name_target_ids(node.get("target_plan")):
                nested_fast_index_names.add(target_id)

        for value in node.values():
            changed += self._visit(value, context, nested_fast_index_names)
        return changed

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        change_count = self._visit(east3_doc, context, set())
        return make_pass_result(changed=change_count > 0, change_count=change_count)
