"""EAST3 swap pattern detection pass.

Detects ``a, b = b, a`` patterns and converts them:
- Name-Name swaps become ``Swap(left, right)`` nodes.
- Subscript-containing swaps are expanded to temporary-variable Assign sequences.
"""

from __future__ import annotations

from typing import Any


def _expr_repr(node: Any) -> str:
    """Generate a simple string key for expression comparison."""
    if not isinstance(node, dict):
        return ""
    kind = node.get("kind", "")
    if kind == "Name":
        return "Name:" + str(node.get("id", ""))
    if kind == "Subscript":
        val = _expr_repr(node.get("value"))
        slc = _expr_repr(node.get("slice"))
        return "Sub:" + val + "[" + slc + "]"
    if kind == "Constant":
        return "Const:" + str(node.get("value", ""))
    if kind == "BinOp":
        left = _expr_repr(node.get("left"))
        right = _expr_repr(node.get("right"))
        op = str(node.get("op", ""))
        return "BinOp:" + left + op + right
    return ""


_swap_tmp_counter: list[int] = [0]


def _fresh_swap_tmp() -> str:
    idx = _swap_tmp_counter[0]
    _swap_tmp_counter[0] = idx + 1
    return "__swap_tmp_" + str(idx)


def _is_name_node(node: Any) -> bool:
    return isinstance(node, dict) and node.get("kind") == "Name"


def _expand_subscript_swap(
    left: dict[str, Any],
    right: dict[str, Any],
    span: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Expand a swap that involves Subscript targets into Assign statements."""
    tmp_name = _fresh_swap_tmp()
    base_span: dict[str, Any] = span if isinstance(span, dict) else {}
    # tmp = left (read)
    tmp_target: dict[str, Any] = {"kind": "Name", "id": tmp_name}
    if base_span:
        tmp_target["source_span"] = base_span
    assign_tmp: dict[str, Any] = {
        "kind": "Assign",
        "target": tmp_target,
        "value": left,
        "declare": True,
    }
    if base_span:
        assign_tmp["source_span"] = base_span
    # left = right (write)
    assign_left: dict[str, Any] = {
        "kind": "Assign",
        "target": left,
        "value": right,
    }
    if base_span:
        assign_left["source_span"] = base_span
    # right = tmp (write)
    tmp_ref: dict[str, Any] = {"kind": "Name", "id": tmp_name}
    if base_span:
        tmp_ref["source_span"] = base_span
    assign_right: dict[str, Any] = {
        "kind": "Assign",
        "target": right,
        "value": tmp_ref,
    }
    if base_span:
        assign_right["source_span"] = base_span
    return [assign_tmp, assign_left, assign_right]


def _detect_swap_in_stmts(stmts: list[Any]) -> list[Any]:
    """Walk statement list and replace 2-element swap Assigns.

    Name-Name swaps become Swap nodes.
    Subscript-containing swaps are expanded to temporary-variable Assign sequences.
    """
    result: list[Any] = []
    for stmt in stmts:
        if not isinstance(stmt, dict):
            result.append(stmt)
            continue
        kind = stmt.get("kind", "")

        if kind == "Assign":
            target = stmt.get("target")
            value = stmt.get("value")
            if (isinstance(target, dict) and target.get("kind") == "Tuple"
                    and isinstance(value, dict) and value.get("kind") == "Tuple"):
                t_elems = target.get("elements", target.get("elts", []))
                v_elems = value.get("elements", value.get("elts", []))
                if (isinstance(t_elems, list) and isinstance(v_elems, list)
                        and len(t_elems) == 2 and len(v_elems) == 2):
                    # Check if it's a swap: a,b = b,a
                    t0 = _expr_repr(t_elems[0])
                    t1 = _expr_repr(t_elems[1])
                    v0 = _expr_repr(v_elems[0])
                    v1 = _expr_repr(v_elems[1])
                    if t0 != "" and t1 != "" and t0 == v1 and t1 == v0:
                        span = stmt.get("source_span")
                        # Name-Name: emit Swap node
                        if _is_name_node(t_elems[0]) and _is_name_node(t_elems[1]):
                            swap: dict[str, Any] = {
                                "kind": "Swap",
                                "left": t_elems[0],
                                "right": t_elems[1],
                                "lhs": t_elems[0],
                                "rhs": t_elems[1],
                            }
                            if isinstance(span, dict):
                                swap["source_span"] = span
                            result.append(swap)
                            continue
                        # Subscript or other: expand to Assign sequence
                        expanded = _expand_subscript_swap(
                            t_elems[0], t_elems[1], span,
                        )
                        result.extend(expanded)
                        continue

        # Recurse into nested blocks
        if kind in ("If", "While", "For", "ForRange", "ForCore"):
            body = stmt.get("body")
            if isinstance(body, list):
                stmt["body"] = _detect_swap_in_stmts(body)
            orelse = stmt.get("orelse")
            if isinstance(orelse, list):
                stmt["orelse"] = _detect_swap_in_stmts(orelse)
        elif kind == "FunctionDef":
            body = stmt.get("body")
            if isinstance(body, list):
                stmt["body"] = _detect_swap_in_stmts(body)
        elif kind == "ClassDef":
            body = stmt.get("body")
            if isinstance(body, list):
                stmt["body"] = _detect_swap_in_stmts(body)
        elif kind == "Try":
            for key in ("body", "orelse", "finalbody"):
                nested = stmt.get(key)
                if isinstance(nested, list):
                    stmt[key] = _detect_swap_in_stmts(nested)
            handlers = stmt.get("handlers")
            if isinstance(handlers, list):
                for h in handlers:
                    if isinstance(h, dict):
                        hbody = h.get("body")
                        if isinstance(hbody, list):
                            h["body"] = _detect_swap_in_stmts(hbody)

        result.append(stmt)
    return result


def detect_swap_patterns(module: dict[str, Any]) -> dict[str, Any]:
    """Top-level entry: detect swap patterns in an EAST3 Module.

    Mutates *module* in place and returns it.
    """
    body = module.get("body")
    if isinstance(body, list):
        module["body"] = _detect_swap_in_stmts(body)
    return module
