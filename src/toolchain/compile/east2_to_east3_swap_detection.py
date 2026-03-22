"""EAST3 swap pattern detection pass.

Detects ``a, b = b, a`` patterns (including Subscript targets) and
converts them to ``Swap(lhs, rhs)`` nodes.
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


def _detect_swap_in_stmts(stmts: list[Any]) -> list[Any]:
    """Walk statement list and replace 2-element swap Assigns with Swap nodes."""
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
                        swap: dict[str, Any] = {
                            "kind": "Swap",
                            "lhs": t_elems[0],
                            "rhs": t_elems[1],
                        }
                        span = stmt.get("source_span")
                        if isinstance(span, dict):
                            swap["source_span"] = span
                        result.append(swap)
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
