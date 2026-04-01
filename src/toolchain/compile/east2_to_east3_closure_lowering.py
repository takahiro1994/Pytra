"""EAST2 -> EAST3 closure lowering for the legacy pipeline."""

from __future__ import annotations

from typing import Any


def _kind(node: Any) -> str:
    if isinstance(node, dict):
        kind = node.get("kind")
        if isinstance(kind, str):
            return kind
    return ""


def _str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _is_function_like_kind(kind: str) -> bool:
    return kind in ("FunctionDef", "ClosureDef")


def _closure_callable_type(node: dict[str, Any]) -> str:
    arg_order = node.get("arg_order")
    arg_types = node.get("arg_types")
    params: list[str] = []
    if isinstance(arg_order, list) and isinstance(arg_types, dict):
        for arg in arg_order:
            if not isinstance(arg, str) or arg == "" or arg == "self":
                continue
            arg_type = arg_types.get(arg)
            params.append(arg_type if isinstance(arg_type, str) and arg_type != "" else "unknown")
    ret = _str(node.get("return_type"))
    if ret == "":
        ret = "unknown"
    return "callable[[" + ",".join(params) + "]," + ret + "]"


def _collect_assign_names(stmt: dict[str, Any], out: dict[str, str]) -> None:
    target = stmt.get("target")
    if not isinstance(target, dict):
        targets = stmt.get("targets")
        if isinstance(targets, list) and len(targets) == 1 and isinstance(targets[0], dict):
            target = targets[0]
    inferred_type = ""
    if _kind(stmt) == "AnnAssign":
        inferred_type = _str(stmt.get("decl_type")) or _str(stmt.get("annotation"))
    elif _kind(stmt) == "Assign":
        inferred_type = _expr_resolved_type(stmt.get("value"))
    _collect_target_local_types(target, inferred_type, out)


def _expr_resolved_type(node: Any) -> str:
    if isinstance(node, dict):
        value = node.get("resolved_type")
        if isinstance(value, str):
            return value
    return ""


def _collect_target_local_types(target: Any, inferred_type: str, out: dict[str, str]) -> None:
    if not isinstance(target, dict):
        return
    kind = _kind(target)
    if kind == "Name":
        name = _str(target.get("id"))
        if name != "" and name not in out:
            target_type = _expr_resolved_type(target)
            out[name] = target_type if target_type != "" else inferred_type
        return
    if kind == "Tuple":
        elements = target.get("elements")
        if isinstance(elements, list):
            for elem in elements:
                _collect_target_local_types(elem, inferred_type, out)


def _collect_target_plan_local_types(target_plan: Any, out: dict[str, str]) -> None:
    if not isinstance(target_plan, dict):
        return
    kind = _kind(target_plan)
    if kind == "NameTarget":
        name = _str(target_plan.get("id"))
        if name != "" and name not in out:
            out[name] = _str(target_plan.get("target_type"))
        return
    if kind == "TupleTarget":
        elements = target_plan.get("elements")
        if isinstance(elements, list):
            for elem in elements:
                _collect_target_plan_local_types(elem, out)


def _collect_function_locals(stmts: list[Any], out: dict[str, str]) -> None:
    for stmt in stmts:
        if not isinstance(stmt, dict):
            continue
        kind = _kind(stmt)
        if _is_function_like_kind(kind) or kind == "ClassDef":
            name = _str(stmt.get("name"))
            if name != "" and name not in out:
                out[name] = name if kind == "ClassDef" else _closure_callable_type(stmt)
            continue
        if kind == "VarDecl":
            name = _str(stmt.get("name"))
            typ = _str(stmt.get("type"))
            if name != "" and name not in out:
                out[name] = typ
        elif kind in ("Assign", "AnnAssign", "AugAssign"):
            _collect_assign_names(stmt, out)
        elif kind == "For":
            _collect_target_local_types(stmt.get("target"), _str(stmt.get("target_type")), out)
        elif kind == "ForRange":
            _collect_target_local_types(stmt.get("target"), _str(stmt.get("target_type")) or "int64", out)
        elif kind == "ForCore":
            _collect_target_plan_local_types(stmt.get("target_plan"), out)
        elif kind == "With":
            items = stmt.get("items")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    _collect_target_local_types(item.get("optional_vars"), "", out)
        for key in ("body", "orelse", "finalbody"):
            nested = stmt.get(key)
            if isinstance(nested, list):
                _collect_function_locals(nested, out)
        handlers = stmt.get("handlers")
        if isinstance(handlers, list):
            for handler in handlers:
                if not isinstance(handler, dict):
                    continue
                name = _str(handler.get("name"))
                if name != "" and name not in out:
                    out[name] = "BaseException"
                hbody = handler.get("body")
                if isinstance(hbody, list):
                    _collect_function_locals(hbody, out)


def _collect_function_scope_types(func: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    self_name = _str(func.get("name"))
    if self_name != "":
        out[self_name] = _closure_callable_type(func)
    arg_types = func.get("arg_types")
    if isinstance(arg_types, dict):
        for name, value in arg_types.items():
            if isinstance(name, str) and name != "" and isinstance(value, str):
                out[name] = value
    captures = func.get("captures")
    if isinstance(captures, list):
        for capture in captures:
            if not isinstance(capture, dict):
                continue
            name = _str(capture.get("name"))
            typ = _str(capture.get("type"))
            if name != "" and name not in out:
                out[name] = typ
    body = func.get("body")
    if isinstance(body, list):
        _collect_function_locals(body, out)
    return out


def _bump_reassigned(out: dict[str, int], name: str) -> None:
    out[name] = out.get(name, 0) + 1


def _collect_target_write_counts(target: Any, out: dict[str, int]) -> None:
    if not isinstance(target, dict):
        return
    kind = _kind(target)
    if kind == "Name":
        name = _str(target.get("id"))
        if name != "":
            _bump_reassigned(out, name)
        return
    if kind == "Tuple":
        elements = target.get("elements")
        if isinstance(elements, list):
            for elem in elements:
                _collect_target_write_counts(elem, out)


def _collect_target_plan_write_counts(target_plan: Any, out: dict[str, int]) -> None:
    if not isinstance(target_plan, dict):
        return
    kind = _kind(target_plan)
    if kind == "NameTarget":
        name = _str(target_plan.get("id"))
        if name != "":
            _bump_reassigned(out, name)
        return
    if kind == "TupleTarget":
        elements = target_plan.get("elements")
        if isinstance(elements, list):
            for elem in elements:
                _collect_target_plan_write_counts(elem, out)


def _collect_reassigned_lexical(stmts: list[Any], out: dict[str, int]) -> None:
    for stmt in stmts:
        if not isinstance(stmt, dict):
            continue
        kind = _kind(stmt)
        if kind in ("Assign", "AnnAssign"):
            _collect_target_write_counts(stmt.get("target"), out)
        elif kind == "AugAssign":
            _collect_target_write_counts(stmt.get("target"), out)
        elif kind in ("For", "ForRange"):
            _collect_target_write_counts(stmt.get("target"), out)
        elif kind == "ForCore":
            _collect_target_plan_write_counts(stmt.get("target_plan"), out)
        if _is_function_like_kind(kind) or kind == "ClassDef":
            continue
        for key in ("body", "orelse", "finalbody"):
            nested = stmt.get(key)
            if isinstance(nested, list):
                _collect_reassigned_lexical(nested, out)
        handlers = stmt.get("handlers")
        if isinstance(handlers, list):
            for handler in handlers:
                if not isinstance(handler, dict):
                    continue
                hbody = handler.get("body")
                if isinstance(hbody, list):
                    _collect_reassigned_lexical(hbody, out)


def _collect_function_reassigned_names(func: dict[str, Any]) -> set[str]:
    counts: dict[str, int] = {}
    body = func.get("body")
    if isinstance(body, list):
        _collect_reassigned_lexical(body, counts)
    out: set[str] = set()
    param_names: set[str] = set()
    arg_order = func.get("arg_order")
    if isinstance(arg_order, list):
        for arg in arg_order:
            if isinstance(arg, str) and arg != "":
                param_names.add(arg)
    for name, count in counts.items():
        if name in param_names or count > 1:
            out.add(name)
    return out


def _collect_name_refs_lexical(node: Any, out: set[str], *, descend_into_root: bool = True) -> None:
    if isinstance(node, list):
        for item in node:
            _collect_name_refs_lexical(item, out, descend_into_root=True)
        return
    if not isinstance(node, dict):
        return
    kind = _kind(node)
    if not descend_into_root and (_is_function_like_kind(kind) or kind == "ClassDef"):
        return
    if kind == "Name":
        name = _str(node.get("id"))
        if name != "":
            out.add(name)
    for key, value in node.items():
        if key == "body" and (_is_function_like_kind(kind) or kind == "ClassDef"):
            if descend_into_root and isinstance(value, list):
                for item in value:
                    _collect_name_refs_lexical(item, out, descend_into_root=False)
            continue
        if isinstance(value, dict) or isinstance(value, list):
            _collect_name_refs_lexical(value, out, descend_into_root=True)


def _closure_capture_entries(
    visible_types: dict[str, str],
    visible_mutable: set[str],
    func: dict[str, Any],
) -> tuple[list[dict[str, Any]], bool]:
    local_types = _collect_function_scope_types(func)
    used_names: set[str] = set()
    defaults = func.get("arg_defaults")
    if isinstance(defaults, dict):
        _collect_name_refs_lexical(defaults, used_names, descend_into_root=True)
    body = func.get("body")
    if isinstance(body, list):
        for stmt in body:
            _collect_name_refs_lexical(stmt, used_names, descend_into_root=False)
    captures: list[dict[str, Any]] = []
    for name in sorted(used_names):
        if name in local_types or name not in visible_types:
            continue
        captures.append(
            {
                "name": name,
                "mode": "mutable" if name in visible_mutable else "readonly",
                "type": visible_types.get(name, ""),
            }
        )
    return captures, _str(func.get("name")) in used_names


def _lower_closure_stmt_list(
    stmts: list[Any],
    visible_types: dict[str, str],
    visible_mutable: set[str],
) -> list[Any]:
    result: list[Any] = []
    for stmt in stmts:
        if not isinstance(stmt, dict):
            result.append(stmt)
            continue
        kind = _kind(stmt)
        if kind == "FunctionDef":
            captures, is_recursive = _closure_capture_entries(visible_types, visible_mutable, stmt)
            stmt["kind"] = "ClosureDef"
            stmt["captures"] = captures
            stmt["capture_types"] = {capture["name"]: capture["type"] for capture in captures if capture.get("name")}
            stmt["capture_modes"] = {capture["name"]: capture["mode"] for capture in captures if capture.get("name")}
            if is_recursive:
                stmt["is_recursive"] = True
            _lower_closure_function(stmt, visible_types, visible_mutable)
            result.append(stmt)
            continue
        if kind == "ClassDef":
            body = stmt.get("body")
            if isinstance(body, list):
                class_visible = dict(visible_types)
                class_name = _str(stmt.get("name"))
                if class_name != "":
                    class_visible[class_name] = class_name
                stmt["body"] = _lower_closure_stmt_list(body, class_visible, visible_mutable)
            result.append(stmt)
            continue
        for key in ("body", "orelse", "finalbody"):
            nested = stmt.get(key)
            if isinstance(nested, list):
                stmt[key] = _lower_closure_stmt_list(nested, visible_types, visible_mutable)
        handlers = stmt.get("handlers")
        if isinstance(handlers, list):
            for handler in handlers:
                if not isinstance(handler, dict):
                    continue
                hbody = handler.get("body")
                if isinstance(hbody, list):
                    handler["body"] = _lower_closure_stmt_list(hbody, visible_types, visible_mutable)
        result.append(stmt)
    return result


def _lower_closure_function(
    func: dict[str, Any],
    outer_visible_types: dict[str, str],
    outer_visible_mutable: set[str],
) -> None:
    body = func.get("body")
    if not isinstance(body, list):
        return
    current_visible = dict(outer_visible_types)
    current_visible.update(_collect_function_scope_types(func))
    current_mutable = set(outer_visible_mutable)
    current_mutable.update(_collect_function_reassigned_names(func))
    func["body"] = _lower_closure_stmt_list(body, current_visible, current_mutable)


def lower_nested_function_defs(module: dict[str, Any]) -> dict[str, Any]:
    body = module.get("body")
    if not isinstance(body, list):
        return module
    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        kind = _kind(stmt)
        if _is_function_like_kind(kind):
            _lower_closure_function(stmt, {}, set())
        elif kind == "ClassDef":
            class_body = stmt.get("body")
            if isinstance(class_body, list):
                stmt["body"] = _lower_closure_stmt_list(class_body, {}, set())
    return module
