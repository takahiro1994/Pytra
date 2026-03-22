"""EAST3 ListComp lowering pass.

Converts ListComp (list comprehension) expressions into equivalent
statement sequences: make empty list + for loop + append.

Before (as expression in Assign):
    grid = [expr for var in iterable]

After (statement sequence replacing the Assign):
    __comp_1: list[T] = []
    for var in iterable:
        __comp_1.append(expr)
    grid = __comp_1

This pass operates on statement lists, replacing Assign/AnnAssign nodes
whose value is a ListComp with the expanded sequence.
"""

from __future__ import annotations

import copy
from typing import Any


_comp_counter: list[int] = [0]


def _next_comp_name() -> str:
    _comp_counter[0] += 1
    return "__comp_" + str(_comp_counter[0])


def _safe_str(v: Any) -> str:
    if isinstance(v, str):
        return v.strip()
    return ""


def _lower_listcomp_in_stmts(stmts: list[Any]) -> list[Any]:
    """Walk statement list and expand ListComp assignments."""
    result: list[Any] = []
    for stmt in stmts:
        if not isinstance(stmt, dict):
            result.append(stmt)
            continue
        kind = stmt.get("kind", "")

        # Check if this is an Assign/AnnAssign with a ListComp value
        if kind in ("Assign", "AnnAssign"):
            value = stmt.get("value")
            if isinstance(value, dict) and value.get("kind") == "ListComp":
                expanded = _expand_listcomp_assign(stmt, value)
                result.extend(expanded)
                continue

        # Check Expr with ListComp (standalone comprehension)
        if kind == "Expr":
            expr_val = stmt.get("value")
            if isinstance(expr_val, dict) and expr_val.get("kind") == "ListComp":
                # Standalone listcomp — expand but discard result
                tmp = _next_comp_name()
                expanded = _expand_listcomp_to_stmts(expr_val, tmp)
                result.extend(expanded)
                continue

        # Recurse into nested blocks
        _recurse_lower_stmts(stmt)
        result.append(stmt)
    return result


def _recurse_lower_stmts(stmt: dict[str, Any]) -> None:
    """Recurse into nested statement blocks."""
    for key in ("body", "orelse", "finalbody"):
        nested = stmt.get(key)
        if isinstance(nested, list):
            stmt[key] = _lower_listcomp_in_stmts(nested)
    if stmt.get("kind") == "Try":
        handlers = stmt.get("handlers")
        if isinstance(handlers, list):
            for h in handlers:
                if isinstance(h, dict):
                    hbody = h.get("body")
                    if isinstance(hbody, list):
                        h["body"] = _lower_listcomp_in_stmts(hbody)


def _expand_listcomp_assign(
    assign_stmt: dict[str, Any],
    listcomp: dict[str, Any],
) -> list[dict[str, Any]]:
    """Expand an Assign whose value is a ListComp into statements."""
    target = assign_stmt.get("target")
    if isinstance(target, dict) and target.get("kind") == "Name":
        target_name = _safe_str(target.get("id"))
    else:
        target_name = ""

    # Use the target name directly if possible, otherwise use a temp
    comp_name = target_name if target_name != "" else _next_comp_name()
    stmts = _expand_listcomp_to_stmts(listcomp, comp_name)

    # If we used a temp name, add final assignment
    if comp_name != target_name and target_name != "":
        stmts.append({
            "kind": "Assign",
            "target": copy.deepcopy(target),
            "value": {"kind": "Name", "id": comp_name, "resolved_type": _safe_str(listcomp.get("resolved_type"))},
        })
    return stmts


def _expand_listcomp_to_stmts(
    listcomp: dict[str, Any],
    result_name: str,
) -> list[dict[str, Any]]:
    """Expand a ListComp node into a list of statements."""
    resolved_type = _safe_str(listcomp.get("resolved_type"))
    if resolved_type in ("", "unknown"):
        resolved_type = "list[object]"

    # 1. Initialize empty list
    init: dict[str, Any] = {
        "kind": "AnnAssign",
        "target": {
            "kind": "Name",
            "id": result_name,
            "resolved_type": resolved_type,
        },
        "annotation": resolved_type,
        "decl_type": resolved_type,
        "declare": True,
        "value": {
            "kind": "List",
            "elements": [],
            "resolved_type": resolved_type,
        },
    }

    # 2. Build nested for loops from generators
    elt = listcomp.get("elt")
    generators = listcomp.get("generators", [])
    if not isinstance(generators, list):
        generators = []

    # Innermost body: append elt to result
    append_stmt: dict[str, Any] = {
        "kind": "Expr",
        "value": {
            "kind": "Call",
            "func": {
                "kind": "Attribute",
                "value": {"kind": "Name", "id": result_name, "resolved_type": resolved_type},
                "attr": "append",
            },
            "args": [copy.deepcopy(elt)] if elt is not None else [],
            "resolved_type": "None",
        },
    }

    # Build for loops from inside out
    body: list[dict[str, Any]] = [append_stmt]

    # Handle conditionals (ifs in generator)
    for gen in reversed(generators):
        if not isinstance(gen, dict):
            continue

        # Wrap body in if-conditions (if any)
        ifs = gen.get("ifs")
        if isinstance(ifs, list) and len(ifs) > 0:
            for cond in reversed(ifs):
                if isinstance(cond, dict):
                    body = [{
                        "kind": "If",
                        "test": copy.deepcopy(cond),
                        "body": body,
                        "orelse": [],
                    }]

        # Build For/ForRange loop
        target = gen.get("target")
        iter_expr = gen.get("iter")
        if isinstance(iter_expr, dict) and iter_expr.get("kind") in ("RangeExpr", "ForRange"):
            # range() → ForRange-style loop
            for_stmt: dict[str, Any] = {
                "kind": "ForRange",
                "target": copy.deepcopy(target) if target else {"kind": "Name", "id": "_"},
                "start": copy.deepcopy(iter_expr.get("start", {"kind": "Constant", "value": 0, "resolved_type": "int64"})),
                "stop": copy.deepcopy(iter_expr.get("stop", iter_expr.get("args", [{}])[0] if isinstance(iter_expr.get("args"), list) and len(iter_expr.get("args", [])) > 0 else {"kind": "Constant", "value": 0})),
                "step": copy.deepcopy(iter_expr.get("step", {"kind": "Constant", "value": 1, "resolved_type": "int64"})),
                "body": body,
                "orelse": [],
            }
        else:
            for_stmt = {
                "kind": "For",
                "target": copy.deepcopy(target) if target else {"kind": "Name", "id": "_"},
                "iter": copy.deepcopy(iter_expr) if iter_expr else {"kind": "Name", "id": "__empty"},
                "body": body,
                "orelse": [],
            }
        body = [for_stmt]

    return [init] + body


def lower_listcomp(module: dict[str, Any]) -> dict[str, Any]:
    """Top-level entry: lower ListComp nodes in an EAST3 Module.

    Mutates *module* in place and returns it.
    """
    _comp_counter[0] = 0
    body = module.get("body")
    if isinstance(body, list):
        module["body"] = _lower_listcomp_in_stmts(body)
    return module
