"""EAST3 main_guard_body discard pass.

Marks Expr Call nodes in main_guard_body with ``discard_result: true``
so emitters know to suppress the return value.
"""

from __future__ import annotations

from typing import Any


def _mark_discard_in_stmts(stmts: list[Any]) -> None:
    """Mark Expr(Call) nodes with discard_result."""
    for stmt in stmts:
        if not isinstance(stmt, dict):
            continue
        if stmt.get("kind") == "Expr":
            value = stmt.get("value")
            if isinstance(value, dict) and value.get("kind") == "Call":
                stmt["discard_result"] = True


def mark_main_guard_discard(module: dict[str, Any]) -> dict[str, Any]:
    """Mark Expr Call nodes in main_guard_body with discard_result=true."""
    # main_guard_body is stored directly on the module
    main_guard = module.get("main_guard_body")
    if isinstance(main_guard, list):
        _mark_discard_in_stmts(main_guard)

    # Also check FunctionDefs named __pytra_main (renamed main)
    body = module.get("body")
    if isinstance(body, list):
        for stmt in body:
            if isinstance(stmt, dict) and stmt.get("kind") == "FunctionDef":
                name = stmt.get("name", "")
                if name == "__pytra_main":
                    fn_body = stmt.get("body")
                    if isinstance(fn_body, list):
                        _mark_discard_in_stmts(fn_body)
    return module
