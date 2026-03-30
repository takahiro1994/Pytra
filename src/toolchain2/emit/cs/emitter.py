"""EAST3 → C# source emitter.

Minimal toolchain2 C# emitter built on CommonRenderer.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from pytra.std.json import JsonVal
from pytra.std.pathlib import Path

from toolchain2.emit.common.code_emitter import (
    RuntimeMapping, load_runtime_mapping, resolve_runtime_call,
    should_skip_module, build_import_alias_map, build_runtime_import_map,
)
from toolchain2.emit.common.common_renderer import CommonRenderer
from toolchain2.emit.common.profile_loader import load_profile_doc
from toolchain2.emit.cs.types import _safe_cs_ident, cs_type, cs_zero_value
from toolchain2.link.expand_defaults import expand_cross_module_defaults


@dataclass
class EmitContext:
    module_id: str = ""
    source_path: str = ""
    is_entry: bool = False
    indent_level: int = 0
    lines: list[str] = field(default_factory=list)
    mapping: RuntimeMapping = field(default_factory=RuntimeMapping)
    import_alias_modules: dict[str, str] = field(default_factory=dict)
    runtime_imports: dict[str, str] = field(default_factory=dict)
    var_types: dict[str, str] = field(default_factory=dict)
    current_return_type: str = ""
    current_class_name: str = ""
    class_names: set[str] = field(default_factory=set)
    class_bases: dict[str, str] = field(default_factory=dict)
    renamed_symbols: dict[str, str] = field(default_factory=dict)
    temp_index: int = 0
    current_base_class_name: str = ""


def _str(node: JsonVal, key: str) -> str:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, str):
            return value
    return ""


def _bool(node: JsonVal, key: str) -> bool:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, bool):
            return value
    return False


def _list(node: JsonVal, key: str) -> list[JsonVal]:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, list):
            return value
    return []


def _dict(node: JsonVal, key: str) -> dict[str, JsonVal]:
    if isinstance(node, dict):
        value = node.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _module_class_name(module_id: str) -> str:
    if module_id == "":
        return "Module"
    tail = module_id.split(".")[-1]
    safe = _safe_cs_ident(tail)
    if safe == "":
        return "Module"
    return safe[0].upper() + safe[1:]


def _safe_name(ctx: EmitContext, name: str) -> str:
    if name == "self":
        return "this"
    renamed = ctx.renamed_symbols.get(name, "")
    if renamed != "":
        return _safe_cs_ident(renamed)
    return _safe_cs_ident(name)


def _next_temp(ctx: EmitContext, prefix: str) -> str:
    ctx.temp_index += 1
    return _safe_cs_ident(prefix + "_" + str(ctx.temp_index))


def _quote_string(value: str) -> str:
    return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\""


def _target_type_from_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    for key in ("decl_type", "annotation", "resolved_type"):
        text = _str(node, key)
        if text != "":
            return _render_type(ctx, text)
    target = node.get("target")
    if isinstance(target, dict):
        rt = _str(target, "resolved_type")
        if rt != "":
            return _render_type(ctx, rt)
    return "object"


def _render_type(ctx: EmitContext, resolved_type: str, *, for_return: bool = False) -> str:
    if resolved_type in ctx.class_names:
        return _safe_name(ctx, resolved_type)
    if resolved_type in ctx.import_alias_modules:
        module_id = ctx.import_alias_modules.get(resolved_type, "")
        if module_id != "" and not should_skip_module(module_id, ctx.mapping):
            return _module_class_name(module_id) + "." + _safe_name(ctx, resolved_type)
    return cs_type(resolved_type, mapping=ctx.mapping, for_return=for_return)


def _arg_order_and_types(node: dict[str, JsonVal]) -> tuple[list[str], dict[str, str]]:
    arg_order: list[str] = []
    for item in _list(node, "arg_order"):
        if isinstance(item, str):
            arg_order.append(item)
    arg_types: dict[str, str] = {}
    for key, value in _dict(node, "arg_types").items():
        if isinstance(key, str) and isinstance(value, str):
            arg_types[key] = value
    return (arg_order, arg_types)


def _emit_constant(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    _ = ctx
    value = node.get("value")
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _quote_string(value)
    return str(value)


def _emit_name(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return _safe_name(ctx, _str(node, "id"))


def _render_list_literal(ctx: EmitContext, node: dict[str, JsonVal], *, preferred_type: str = "") -> str:
    elems = _list(node, "elements")
    rt = preferred_type if preferred_type != "" else _str(node, "resolved_type")
    out_type = "List<object>"
    if rt != "":
        out_type = _render_type(ctx, rt)
    rendered = [_emit_expr(ctx, elem) for elem in elems]
    if len(rendered) == 0:
        return "new " + out_type + "()"
    return "new " + out_type + " { " + ", ".join(rendered) + " }"


def _render_set_literal(ctx: EmitContext, node: dict[str, JsonVal], *, preferred_type: str = "") -> str:
    elems = _list(node, "elements")
    rt = preferred_type if preferred_type != "" else _str(node, "resolved_type")
    out_type = "HashSet<object>"
    if rt != "":
        out_type = _render_type(ctx, rt)
    rendered = [_emit_expr(ctx, elem) for elem in elems]
    if len(rendered) == 0:
        return "new " + out_type + "()"
    return "new " + out_type + " { " + ", ".join(rendered) + " }"


def _render_dict_literal(ctx: EmitContext, node: dict[str, JsonVal], *, preferred_type: str = "") -> str:
    entries = _list(node, "entries")
    rt = preferred_type if preferred_type != "" else _str(node, "resolved_type")
    out_type = "Dictionary<object, object>"
    if rt != "":
        out_type = _render_type(ctx, rt)
    rendered_entries: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rendered_entries.append("{ " + _emit_expr(ctx, entry.get("key")) + ", " + _emit_expr(ctx, entry.get("value")) + " }")
    if len(rendered_entries) == 0:
        return "new " + out_type + "()"
    return "new " + out_type + " { " + ", ".join(rendered_entries) + " }"


def _render_subscript(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner_node = node.get("value")
    owner = _emit_expr(ctx, owner_node)
    owner_type = _str(owner_node, "resolved_type") if isinstance(owner_node, dict) else ""
    slice_node = node.get("slice")
    if isinstance(slice_node, dict) and _str(slice_node, "kind") == "Slice":
        lower = slice_node.get("lower")
        upper = slice_node.get("upper")
        lower_expr = _emit_expr(ctx, lower) if isinstance(lower, dict) else "null"
        upper_expr = _emit_expr(ctx, upper) if isinstance(upper, dict) else "null"
        return "py_runtime.py_slice(" + owner + ", " + lower_expr + ", " + upper_expr + ")"
    index = _emit_expr(ctx, slice_node)
    if owner_type.startswith("list[") or owner_type == "str":
        return "py_runtime.py_get(" + owner + ", " + index + ")"
    return owner + "[" + index + "]"


def _render_ifexp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    test = _emit_condition_expr(ctx, node.get("test"), wrap=False)
    body = _emit_expr(ctx, node.get("body"))
    orelse = _emit_expr(ctx, node.get("orelse"))
    return "(" + test + " ? " + body + " : " + orelse + ")"


def _emit_formatted_value(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    return "Convert.ToString(" + _emit_expr(ctx, node.get("value")) + ")"


def _emit_fstring(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    parts: list[str] = []
    for value in _list(node, "values"):
        if not isinstance(value, dict):
            continue
        kind = _str(value, "kind")
        if kind == "Constant":
            raw = value.get("value")
            if isinstance(raw, str):
                parts.append(_quote_string(raw))
            continue
        if kind == "FormattedValue":
            parts.append(_emit_formatted_value(ctx, value))
            continue
        parts.append("Convert.ToString(" + _emit_expr(ctx, value) + ")")
    if len(parts) == 0:
        return "\"\""
    if len(parts) == 1:
        return parts[0]
    return "(" + " + ".join(parts) + ")"


def _emit_box(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    value = node.get("value")
    if isinstance(value, dict) and _str(value, "resolved_type") == "Callable":
        return "new Action(" + _emit_expr(ctx, value) + ")"
    return _emit_expr(ctx, value)


def _emit_lambda(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    arg_order, arg_types = _arg_order_and_types(node)
    if len(arg_order) == 0:
        for arg in _list(node, "args"):
            if isinstance(arg, dict):
                arg_name = _str(arg, "arg")
                if arg_name != "":
                    arg_order.append(arg_name)
                    if arg_name not in arg_types:
                        arg_types[arg_name] = _str(arg, "resolved_type")
    params: list[str] = []
    for raw_arg_name in arg_order:
        arg_name = _safe_name(ctx, raw_arg_name)
        params.append(_render_type(ctx, arg_types.get(raw_arg_name, "")) + " " + arg_name)
    return "(" + ", ".join(params) + ") => " + _emit_expr(ctx, node.get("body"))


def _super_ctor_call(node: dict[str, JsonVal]) -> tuple[bool, list[str]]:
    body = _list(node, "body")
    if len(body) == 0:
        return (False, [])
    first = body[0]
    if not isinstance(first, dict) or _str(first, "kind") != "Expr":
        return (False, [])
    value = first.get("value")
    if not isinstance(value, dict) or _str(value, "kind") != "Call":
        return (False, [])
    func = value.get("func")
    if not isinstance(func, dict) or _str(func, "kind") != "Attribute" or _str(func, "attr") != "__init__":
        return (False, [])
    owner = func.get("value")
    if not isinstance(owner, dict) or _str(owner, "kind") != "Call":
        return (False, [])
    owner_func = owner.get("func")
    if not isinstance(owner_func, dict) or _str(owner_func, "kind") != "Name" or _str(owner_func, "id") != "super":
        return (False, [])
    return (True, [_emit_expr(EmitContext(mapping=node.get("mapping", RuntimeMapping())), arg) for arg in _list(value, "args")])


def _emit_attribute(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner = _emit_expr(ctx, node.get("value"))
    attr = _safe_cs_ident(_str(node, "attr"))
    return owner + "." + attr


def _is_module_owner(ctx: EmitContext, node: JsonVal) -> bool:
    if not isinstance(node, dict):
        return False
    owner_id = _str(node, "id")
    return _str(node, "resolved_type") == "module" or owner_id in ctx.import_alias_modules


def _call_builtin_name(node: dict[str, JsonVal]) -> str:
    func = node.get("func")
    if isinstance(func, dict):
        kind = _str(func, "kind")
        if kind == "Name":
            return _str(func, "id")
        if kind == "Attribute":
            return _str(func, "attr")
    return ""


def _render_expr_with_preferred_type(ctx: EmitContext, node: JsonVal, preferred_type: str = "") -> str:
    if not isinstance(node, dict):
        return _emit_expr(ctx, node)
    kind = _str(node, "kind")
    if kind in ("Box", "Unbox"):
        return _render_expr_with_preferred_type(ctx, node.get("value"), preferred_type=preferred_type)
    if kind == "List":
        return _render_list_literal(ctx, node, preferred_type=preferred_type)
    if kind == "Set":
        return _render_set_literal(ctx, node, preferred_type=preferred_type)
    if kind == "Dict":
        return _render_dict_literal(ctx, node, preferred_type=preferred_type)
    return _emit_expr(ctx, node)


def _container_method_call(
    ctx: EmitContext,
    owner_expr: str,
    owner_type: str,
    method_name: str,
    args: list[str],
) -> str:
    if owner_type.startswith("list["):
        if method_name == "append" and len(args) >= 1:
            return "py_runtime.py_append(" + owner_expr + ", " + args[0] + ")"
        if method_name == "pop":
            if len(args) >= 1:
                return "py_runtime.py_pop(" + owner_expr + ", " + args[0] + ")"
            return "py_runtime.py_pop(" + owner_expr + ")"
    if owner_type.startswith("dict["):
        if method_name == "get" and len(args) >= 1:
            default_expr = args[1] if len(args) > 1 else "default"
            temp_name = _next_temp(ctx, "__dict_value")
            return "(" + owner_expr + ".TryGetValue(" + args[0] + ", out var " + temp_name + ") ? " + temp_name + " : " + default_expr + ")"
        if method_name == "keys":
            key_type = "object"
            inner = owner_type[5:-1].strip()
            parts = [part.strip() for part in inner.split(",", 1)]
            if len(parts) >= 1 and parts[0] != "":
                key_type = _render_type(ctx, parts[0])
            return "new List<" + key_type + ">(" + owner_expr + ".Keys)"
        if method_name == "values":
            value_type = "object"
            inner2 = owner_type[5:-1].strip()
            parts2 = [part.strip() for part in inner2.split(",", 1)]
            if len(parts2) == 2 and parts2[1] != "":
                value_type = _render_type(ctx, parts2[1])
            return "new List<" + value_type + ">(" + owner_expr + ".Values)"
    if owner_type.startswith("set["):
        if method_name == "add" and len(args) >= 1:
            return owner_expr + ".Add(" + args[0] + ")"
        if method_name in ("discard", "remove") and len(args) >= 1:
            return owner_expr + ".Remove(" + args[0] + ")"
    if owner_type == "str" and method_name == "join" and len(args) == 1:
        return "string.Join(" + owner_expr + ", " + args[0] + ")"
    return ""


def _emit_builtin_ctor(ctx: EmitContext, func_name: str, node: dict[str, JsonVal], args: list[str]) -> str:
    resolved_ctor_type = _str(node, "resolved_type")
    target_type = _render_type(ctx, resolved_ctor_type if resolved_ctor_type != "" else func_name)
    if func_name == "list":
        if len(args) == 0:
            return "new " + target_type + "()"
        return "new " + target_type + "(" + args[0] + ")"
    if func_name == "dict":
        if len(args) == 0:
            return "new " + target_type + "()"
    if func_name == "set":
        if len(args) == 0:
            return "new " + target_type + "()"
        return "new " + target_type + "(" + args[0] + ")"
    if func_name == "tuple":
        return "new " + target_type + " { " + ", ".join(args) + " }"
    if func_name in ("Exception", "BaseException", "RuntimeError", "ValueError", "TypeError", "IndexError", "KeyError", "NameError"):
        if len(args) == 0:
            return "new " + target_type + "()"
        return "new " + target_type + "(" + ", ".join(args) + ")"
    return "new " + target_type + "(" + ", ".join(args) + ")"


def _emit_call(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    args = [_emit_expr(ctx, arg) for arg in _list(node, "args")]
    runtime_call = _str(node, "runtime_call")
    builtin_name = _call_builtin_name(node)
    adapter = _str(node, "runtime_call_adapter_kind")
    func = node.get("func")
    owner_expr = ""
    owner_type = ""
    prepend_owner = False
    runtime_owner = node.get("runtime_owner")
    if isinstance(runtime_owner, dict):
        owner_expr = _emit_expr(ctx, runtime_owner)
        owner_type = _str(runtime_owner, "resolved_type")
        prepend_owner = True
    if isinstance(func, dict) and _str(func, "kind") == "Attribute":
        owner_node = func.get("value")
        owner_expr = _emit_expr(ctx, owner_node)
        owner_type = _str(owner_node, "resolved_type") if isinstance(owner_node, dict) else owner_type
        prepend_owner = not _is_module_owner(ctx, owner_node)
        attr_name = _str(func, "attr")
        container_call = _container_method_call(ctx, owner_expr, owner_type, attr_name, args)
        if container_call != "":
            return container_call
    if isinstance(func, dict) and _str(func, "kind") == "Name":
        func_name = _str(func, "id")
        if func_name in ctx.runtime_imports and "." in ctx.runtime_imports[func_name]:
            return ctx.runtime_imports[func_name] + "(" + ", ".join(args) + ")"
        if _str(func, "resolved_type") == "type":
            if func_name in ctx.import_alias_modules:
                module_id = ctx.import_alias_modules.get(func_name, "")
                if module_id != "" and not should_skip_module(module_id, ctx.mapping):
                    return "new " + _module_class_name(module_id) + "." + _safe_name(ctx, func_name) + "(" + ", ".join(args) + ")"
            return _emit_builtin_ctor(ctx, func_name, node, args)
        if func_name in ctx.import_alias_modules:
            module_id = ctx.import_alias_modules.get(func_name, "")
            if module_id != "" and not should_skip_module(module_id, ctx.mapping):
                return _module_class_name(module_id) + "." + _safe_name(ctx, func_name) + "(" + ", ".join(args) + ")"
        if owner_expr != "" and func_name in ("append", "pop", "get", "keys", "values", "add", "discard", "remove"):
            owner_call = _container_method_call(ctx, owner_expr, owner_type, func_name, args)
            if owner_call != "":
                return owner_call
    if isinstance(func, dict) and _str(func, "kind") == "Lambda":
        delegate_type = _render_type(ctx, _str(func, "resolved_type"))
        return "((" + delegate_type + ")(" + _emit_expr(ctx, func) + "))(" + ", ".join(args) + ")"
    resolved = ""
    if runtime_call != "" or adapter != "":
        resolved = resolve_runtime_call(runtime_call, builtin_name, adapter, ctx.mapping)
    elif builtin_name in ctx.mapping.calls:
        resolved = resolve_runtime_call(runtime_call, builtin_name, adapter, ctx.mapping)
    if resolved == "__CAST__":
        if len(args) == 1:
            target_type = _render_type(ctx, _str(node, "resolved_type"))
            return "((" + target_type + ")" + args[0] + ")"
        return args[0] if len(args) > 0 else ""
    if resolved != "" and not resolved.startswith("__"):
        call_args = list(args)
        if prepend_owner and owner_expr != "":
            call_args = [owner_expr] + call_args
        return resolved + "(" + ", ".join(call_args) + ")"
    return _emit_expr(ctx, func) + "(" + ", ".join(args) + ")"


def _emit_condition_expr(ctx: EmitContext, node: JsonVal, *, wrap: bool = True) -> str:
    expr = _emit_expr(ctx, node)
    if isinstance(node, dict):
        rt = _str(node, "resolved_type")
        if rt != "" and rt != "bool":
            expr = "py_runtime.py_bool(" + expr + ")"
    if wrap:
        return "(" + expr + ")"
    return expr


def _emit_list_repeat(ctx: EmitContext, left_node: JsonVal, right_node: JsonVal, result_type: str) -> str:
    left_expr = _emit_expr(ctx, left_node)
    right_expr = _emit_expr(ctx, right_node)
    if isinstance(right_node, dict) and _str(right_node, "resolved_type").startswith("list["):
        left_expr, right_expr = right_expr, left_expr
    target_type = _render_type(ctx, result_type)
    return "py_runtime.py_repeat<" + target_type[5:-1] + ">(" + left_expr + ", " + right_expr + ")"


def _emit_binop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    op = _str(node, "op")
    if op == "Mult":
        left_node = node.get("left")
        right_node = node.get("right")
        left_type = _str(left_node, "resolved_type") if isinstance(left_node, dict) else ""
        right_type = _str(right_node, "resolved_type") if isinstance(right_node, dict) else ""
        result_type = _str(node, "resolved_type")
        if left_type.startswith("list[") or right_type.startswith("list["):
            return _emit_list_repeat(ctx, left_node, right_node, result_type)
    return CommonRenderer.render_binop(_CsExprCommonRenderer(ctx), node)


def _emit_compare(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    left_node = node.get("left")
    comparators = _list(node, "comparators")
    ops = _list(node, "ops")
    if len(comparators) == 0 or len(ops) == 0:
        return _emit_expr(ctx, left_node)
    current_left = _emit_expr(ctx, left_node)
    parts: list[str] = []
    for idx, comparator in enumerate(comparators):
        op_obj = ops[idx] if idx < len(ops) else None
        op_name = op_obj if isinstance(op_obj, str) else _str(op_obj, "kind") if isinstance(op_obj, dict) else ""
        right = _emit_expr(ctx, comparator)
        if op_name == "In":
            parts.append("py_runtime.py_in(" + current_left + ", " + right + ")")
        elif op_name == "NotIn":
            parts.append("(!py_runtime.py_in(" + current_left + ", " + right + "))")
        else:
            op_text = {
                "Eq": "==",
                "NotEq": "!=",
                "Lt": "<",
                "LtE": "<=",
                "Gt": ">",
                "GtE": ">=",
                "Is": "==",
                "IsNot": "!=",
            }.get(op_name, op_name)
            parts.append("(" + current_left + " " + op_text + " " + right + ")")
        current_left = right
    if len(parts) == 1:
        return parts[0]
    return "(" + " && ".join(parts) + ")"


def _emit_boolop(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    values = _list(node, "values")
    if len(values) == 0:
        return "false"
    if len(values) == 1:
        return _emit_expr(ctx, values[0])
    rendered = [_emit_expr(ctx, value) for value in values]
    if _str(node, "resolved_type") == "bool":
        op_text = "&&" if _str(node, "op") == "And" else "||"
        wrapped = [_emit_condition_expr(ctx, value, wrap=False) for value in values]
        return "(" + (" " + op_text + " ").join(wrapped) + ")"
    result = rendered[-1]
    for idx in range(len(rendered) - 2, -1, -1):
        current = rendered[idx]
        test = "py_runtime.py_bool(" + current + ")"
        if _str(node, "op") == "And":
            result = "(" + test + " ? " + result + " : " + current + ")"
        else:
            result = "(" + test + " ? " + current + " : " + result + ")"
    return result


def _emit_comprehension(ctx: EmitContext, node: dict[str, JsonVal], comp_kind: str) -> str:
    result_type = _render_type(ctx, _str(node, "resolved_type"))
    result_name = _next_temp(ctx, "__comp")
    iter_name = _next_temp(ctx, "__item")
    lines: list[str] = []
    lines.append("(new Func<" + result_type + ">(() => {")
    if comp_kind == "list":
        lines.append("    " + result_type + " " + result_name + " = new " + result_type + "();")
    else:
        lines.append("    " + result_type + " " + result_name + " = new " + result_type + "();")
    generators = _list(node, "generators")
    depth = 1
    target_expr = ""
    for gen in generators:
        if not isinstance(gen, dict):
            continue
        target = gen.get("target")
        target_name = iter_name
        target_type = "var"
        if isinstance(target, dict) and _str(target, "kind") == "Name":
            raw_name = _str(target, "id")
            if raw_name != "":
                target_name = _safe_name(ctx, raw_name)
            target_rt = _str(target, "resolved_type")
            if target_rt != "":
                target_type = _render_type(ctx, target_rt)
        target_expr = target_name
        iter_expr = _emit_expr(ctx, gen.get("iter"))
        lines.append("    " * depth + "foreach (" + target_type + " " + target_name + " in " + iter_expr + ") {")
        depth += 1
        for if_node in _list(gen, "ifs"):
            lines.append("    " * depth + "if (!" + _emit_condition_expr(ctx, if_node) + ") {")
            lines.append("    " * (depth + 1) + "continue;")
            lines.append("    " * depth + "}")
    if comp_kind == "dict":
        lines.append("    " * depth + result_name + "[" + _emit_expr(ctx, node.get("key")) + "] = " + _emit_expr(ctx, node.get("value")) + ";")
    elif comp_kind == "set":
        lines.append("    " * depth + result_name + ".Add(" + _emit_expr(ctx, node.get("elt")) + ");")
    else:
        lines.append("    " * depth + "py_runtime.py_append(" + result_name + ", " + _emit_expr(ctx, node.get("elt")) + ");")
    for _ in generators:
        depth -= 1
        lines.append("    " * depth + "}")
    lines.append("    return " + result_name + ";")
    lines.append("})())")
    _ = target_expr
    return "\n".join(lines)


def _emit_expr(ctx: EmitContext, node: JsonVal) -> str:
    if not isinstance(node, dict):
        return "null"
    renderer = _CsExprCommonRenderer(ctx)
    return renderer.render_expr(node)


class _CsStmtCommonRenderer(CommonRenderer):
    def __init__(self, ctx: EmitContext) -> None:
        self.ctx = ctx
        super().__init__("cs")
        self.profile = load_profile_doc("cs")
        prec = self.profile.get("operators")
        prec_map: dict[str, int] = {}
        if isinstance(prec, dict):
            raw = prec.get("precedence")
            if isinstance(raw, dict):
                for key, value in raw.items():
                    if isinstance(key, str) and isinstance(value, int):
                        prec_map[key] = value
        self._op_prec_table = prec_map
        self.state.lines = ctx.lines
        self.state.indent_level = ctx.indent_level

    def render_name(self, node: dict[str, JsonVal]) -> str:
        return _emit_name(self.ctx, node)

    def render_constant(self, node: dict[str, JsonVal]) -> str:
        return _emit_constant(self.ctx, node)

    def render_binop(self, node: dict[str, JsonVal]) -> str:
        return _emit_binop(self.ctx, node)

    def render_compare(self, node: dict[str, JsonVal]) -> str:
        return _emit_compare(self.ctx, node)

    def render_boolop(self, node: dict[str, JsonVal]) -> str:
        return _emit_boolop(self.ctx, node)

    def render_expr(self, node: JsonVal) -> str:
        return _emit_expr(self.ctx, node)

    def render_attribute(self, node: dict[str, JsonVal]) -> str:
        return _emit_attribute(self.ctx, node)

    def render_call(self, node: dict[str, JsonVal]) -> str:
        return _emit_call(self.ctx, node)

    def render_assign_stmt(self, node: dict[str, JsonVal]) -> str:
        _ = node
        raise RuntimeError("cs assign string hook is not used directly")

    def render_condition_expr(self, node: JsonVal) -> str:
        return _emit_condition_expr(self.ctx, node)

    def emit_assign_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_assign_stmt(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def emit_return_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        value = node.get("value")
        if isinstance(value, dict):
            self._emit_stmt_line("return " + _emit_expr(self.ctx, value))
        else:
            self._emit_stmt_line("return")
        self.state.indent_level = self.ctx.indent_level

    def emit_expr_stmt(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        self._emit_stmt_line(_emit_expr(self.ctx, node.get("value")))
        self.state.indent_level = self.ctx.indent_level

    def render_raise_value(self, node: dict[str, JsonVal]) -> str:
        exc = node.get("exc")
        if not isinstance(exc, dict):
            return ""
        return _emit_expr(self.ctx, exc)

    def render_except_open(self, handler: dict[str, JsonVal]) -> str:
        name = _str(handler, "name")
        if name == "":
            name = "ex"
        type_node = handler.get("type")
        type_name = "Exception"
        if isinstance(type_node, dict):
            if _str(type_node, "kind") == "Name":
                type_name = cs_type(_str(type_node, "id"), mapping=self.ctx.mapping)
            else:
                type_name = cs_type(_str(type_node, "resolved_type"), mapping=self.ctx.mapping)
        return "catch (" + type_name + " " + _safe_cs_ident(name) + ") {"

    def emit_stmt_extension(self, node: dict[str, JsonVal]) -> None:
        self.ctx.indent_level = self.state.indent_level
        _emit_stmt_extension(self.ctx, node)
        self.state.indent_level = self.ctx.indent_level

    def emit_try_stmt(self, node: dict[str, JsonVal]) -> None:
        body = _list(node, "body")
        handlers = _list(node, "handlers")
        finalbody = _list(node, "finalbody")
        self._emit("try {")
        self.state.indent_level += 1
        self.emit_body(body)
        self.state.indent_level -= 1
        self._emit("}")
        for raw_handler in handlers:
            if not isinstance(raw_handler, dict):
                continue
            self._emit(self.render_except_open(raw_handler))
            self.state.indent_level += 1
            self.emit_try_handler_body(raw_handler)
            self.state.indent_level -= 1
            self._emit("}")
        if len(finalbody) > 0:
            self._emit("finally {")
            self.state.indent_level += 1
            self.emit_body(finalbody)
            self.state.indent_level -= 1
            self._emit("}")


class _CsExprCommonRenderer(CommonRenderer):
    def __init__(self, ctx: EmitContext) -> None:
        self.ctx = ctx
        super().__init__("cs")
        self.profile = load_profile_doc("cs")
        prec = self.profile.get("operators")
        prec_map: dict[str, int] = {}
        if isinstance(prec, dict):
            raw = prec.get("precedence")
            if isinstance(raw, dict):
                for key, value in raw.items():
                    if isinstance(key, str) and isinstance(value, int):
                        prec_map[key] = value
        self._op_prec_table = prec_map

    def render_name(self, node: dict[str, JsonVal]) -> str:
        return _emit_name(self.ctx, node)

    def render_constant(self, node: dict[str, JsonVal]) -> str:
        return _emit_constant(self.ctx, node)

    def render_binop(self, node: dict[str, JsonVal]) -> str:
        return _emit_binop(self.ctx, node)

    def render_compare(self, node: dict[str, JsonVal]) -> str:
        return _emit_compare(self.ctx, node)

    def render_boolop(self, node: dict[str, JsonVal]) -> str:
        return _emit_boolop(self.ctx, node)

    def render_attribute(self, node: dict[str, JsonVal]) -> str:
        return _emit_attribute(self.ctx, node)

    def render_call(self, node: dict[str, JsonVal]) -> str:
        return _emit_call(self.ctx, node)

    def render_assign_stmt(self, node: dict[str, JsonVal]) -> str:
        _ = node
        raise RuntimeError("cs assign hook is not used in expr adapter")

    def render_expr_extension(self, node: dict[str, JsonVal]) -> str:
        kind = _str(node, "kind")
        if kind == "List":
            return _render_list_literal(self.ctx, node)
        if kind == "Set":
            return _render_set_literal(self.ctx, node)
        if kind == "Dict":
            return _render_dict_literal(self.ctx, node)
        if kind == "Subscript":
            return _render_subscript(self.ctx, node)
        if kind == "IfExp":
            return _render_ifexp(self.ctx, node)
        if kind == "Tuple":
            items = [_emit_expr(self.ctx, item) for item in _list(node, "elements")]
            tuple_type = _render_type(self.ctx, _str(node, "resolved_type"))
            return "new " + tuple_type + " { " + ", ".join(items) + " }"
        if kind == "ListComp":
            return _emit_comprehension(self.ctx, node, "list")
        if kind == "SetComp":
            return _emit_comprehension(self.ctx, node, "set")
        if kind == "DictComp":
            return _emit_comprehension(self.ctx, node, "dict")
        if kind == "JoinedStr":
            return _emit_fstring(self.ctx, node)
        if kind == "FormattedValue":
            return _emit_formatted_value(self.ctx, node)
        if kind == "Box":
            return _emit_box(self.ctx, node)
        if kind == "Unbox":
            return _emit_expr(self.ctx, node.get("value"))
        if kind == "Lambda":
            return _emit_lambda(self.ctx, node)
        if kind == "Slice":
            return "null"
        return "/* unsupported:" + kind + " */"


def _emit_assign_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target = node.get("target")
    value = node.get("value")
    target_text = _emit_expr(ctx, target)
    preferred_type = _str(node, "decl_type")
    if preferred_type == "" and isinstance(target, dict):
        preferred_type = _str(target, "resolved_type")
    value_text = _render_expr_with_preferred_type(ctx, value, preferred_type=preferred_type)
    declare = _bool(node, "declare") or _str(node, "kind") == "AnnAssign"
    if isinstance(target, dict) and _str(target, "kind") == "Attribute":
        declare = False
    if isinstance(target, dict) and _str(target, "kind") == "Name":
        if ctx.current_return_type != "" and target_text not in ctx.var_types:
            declare = True
        if target_text in ctx.var_types:
            declare = False
    if declare:
        decl_type = _target_type_from_stmt(ctx, node)
        ctx.var_types[target_text] = decl_type
        ctx.lines.append("    " * ctx.indent_level + decl_type + " " + target_text + " = " + value_text + ";")
        return
    if isinstance(target, dict) and _str(target, "kind") == "Name" and target_text not in ctx.var_types and ctx.current_return_type != "":
        decl_type2 = _target_type_from_stmt(ctx, node)
        ctx.var_types[target_text] = decl_type2
        ctx.lines.append("    " * ctx.indent_level + decl_type2 + " " + target_text + " = " + value_text + ";")
        return
    ctx.lines.append("    " * ctx.indent_level + target_text + " = " + value_text + ";")


def _emit_for_range(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target = _emit_expr(ctx, node.get("target"))
    start = _emit_expr(ctx, node.get("start"))
    stop = _emit_expr(ctx, node.get("stop"))
    step = _emit_expr(ctx, node.get("step"))
    indent = "    " * ctx.indent_level
    loop_cond = target + " < " + stop
    loop_inc = target + " += " + step
    step_text = step.strip()
    if step_text.startswith("-"):
        loop_cond = target + " > " + stop
    ctx.lines.append(indent + "for (long " + target + " = " + start + "; " + loop_cond + "; " + loop_inc + ") {")
    ctx.indent_level += 1
    _emit_stmt_list(ctx, _list(node, "body"))
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")


def _emit_for_each(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target = _emit_expr(ctx, node.get("target"))
    iter_expr = _emit_expr(ctx, node.get("iter"))
    target_type = "var"
    if isinstance(node.get("target"), dict):
        target_rt = _str(node.get("target"), "resolved_type")
        if target_rt != "":
            target_type = cs_type(target_rt, mapping=ctx.mapping)
    indent = "    " * ctx.indent_level
    ctx.lines.append(indent + "foreach (" + target_type + " " + target + " in " + iter_expr + ") {")
    ctx.indent_level += 1
    _emit_stmt_list(ctx, _list(node, "body"))
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")


def _for_target_name_and_type(target_node: JsonVal) -> tuple[str, str]:
    if not isinstance(target_node, dict):
        return ("_item", "")
    kind = _str(target_node, "kind")
    if kind in ("Name", "NameTarget"):
        name = _str(target_node, "id")
        target_type = _str(target_node, "target_type")
        if target_type == "":
            target_type = _str(target_node, "resolved_type")
        return (name, target_type)
    return ("_item", "")


def _emit_for_core(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target_node = node.get("target_plan")
    if target_node is None:
        target_node = node.get("target")
    iter_plan = node.get("iter_plan")
    body = _list(node, "body")
    orelse = _list(node, "orelse")
    target_name, target_type = _for_target_name_and_type(target_node)
    safe_target = _safe_name(ctx, target_name) if target_name not in ("", "_item") else "_item"
    if safe_target != "_item":
        ctx.var_types[safe_target] = target_type
    if isinstance(iter_plan, dict):
        plan_kind = _str(iter_plan, "kind")
        if plan_kind == "StaticRangeForPlan":
            range_node = dict(iter_plan)
            range_node["target"] = {"kind": "Name", "id": safe_target, "resolved_type": target_type}
            range_node["body"] = body
            _emit_for_range(ctx, range_node)
            if len(orelse) > 0:
                _emit_stmt_list(ctx, orelse)
            return
        if plan_kind == "RuntimeIterForPlan":
            temp_node = {
                "kind": "For",
                "target": {"kind": "Name", "id": safe_target, "resolved_type": target_type},
                "iter": iter_plan.get("iter_expr"),
                "body": body,
            }
            _emit_for_each(ctx, temp_node)
            if len(orelse) > 0:
                _emit_stmt_list(ctx, orelse)
            return
    temp_node2 = {
        "kind": "For",
        "target": {"kind": "Name", "id": safe_target, "resolved_type": target_type},
        "iter": node.get("iter"),
        "body": body,
    }
    _emit_for_each(ctx, temp_node2)
    if len(orelse) > 0:
        _emit_stmt_list(ctx, orelse)


def _emit_aug_assign_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    symbol = {
        "Add": "+",
        "Sub": "-",
        "Mult": "*",
        "Div": "/",
        "BitAnd": "&",
        "BitOr": "|",
        "BitXor": "^",
        "LShift": "<<",
        "RShift": ">>",
    }.get(_str(node, "op"), "+")
    target_text = _emit_expr(ctx, node.get("target"))
    value_text = _emit_expr(ctx, node.get("value"))
    ctx.lines.append("    " * ctx.indent_level + target_text + " " + symbol + "= " + value_text + ";")


def _emit_function(ctx: EmitContext, node: dict[str, JsonVal], *, force_public: bool = True, static_method: bool = True) -> None:
    name = _safe_name(ctx, _str(node, "name"))
    return_type = _str(node, "return_type")
    if return_type == "":
        return_type = "None"
    saved_var_types = dict(ctx.var_types)
    ctx.current_return_type = return_type
    arg_order, arg_types = _arg_order_and_types(node)
    params: list[str] = []
    for idx, raw_arg_name in enumerate(arg_order):
        if ctx.current_class_name != "" and idx == 0 and raw_arg_name == "self":
            continue
        arg_name = _safe_name(ctx, raw_arg_name)
        src_type = ""
        arg_type = arg_types.get(raw_arg_name)
        if isinstance(arg_type, str):
            src_type = arg_type
        if src_type == "":
            src_type = "object"
        ctx.var_types[arg_name] = src_type
        params.append(_render_type(ctx, src_type) + " " + arg_name)
    modifiers: list[str] = []
    if force_public:
        modifiers.append("public")
    if static_method:
        modifiers.append("static")
    indent = "    " * ctx.indent_level
    body = _list(node, "body")
    if ctx.current_class_name != "" and _str(node, "name") == "__init__":
        base_init = ""
        if len(body) > 0 and ctx.current_base_class_name != "":
            first = body[0]
            if isinstance(first, dict) and _str(first, "kind") == "Expr":
                value = first.get("value")
                if isinstance(value, dict) and _str(value, "kind") == "Call":
                    func = value.get("func")
                    if isinstance(func, dict) and _str(func, "kind") == "Attribute" and _str(func, "attr") == "__init__":
                        owner = func.get("value")
                        if isinstance(owner, dict) and _str(owner, "kind") == "Call":
                            owner_func = owner.get("func")
                            if isinstance(owner_func, dict) and _str(owner_func, "kind") == "Name" and _str(owner_func, "id") == "super":
                                base_init = " : base(" + ", ".join(_emit_expr(ctx, arg) for arg in _list(value, "args")) + ")"
                                body = body[1:]
        ctx.lines.append(indent + "public " + ctx.current_class_name + "(" + ", ".join(params) + ")" + base_init + " {")
    else:
        signature = " ".join(modifiers + [_render_type(ctx, return_type, for_return=True), name])
        ctx.lines.append(indent + signature + "(" + ", ".join(params) + ") {")
    ctx.indent_level += 1
    _emit_stmt_list(ctx, body)
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")
    ctx.var_types = saved_var_types


def _emit_class(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _safe_name(ctx, _str(node, "name"))
    indent = "    " * ctx.indent_level
    base_name = _str(node, "base")
    base_spec = ""
    if base_name != "" and base_name != "object":
        base_spec = " : " + _render_type(ctx, base_name)
    ctx.lines.append(indent + "public sealed class " + name + base_spec + " {")
    ctx.indent_level += 1
    previous_class = ctx.current_class_name
    previous_base_class = ctx.current_base_class_name
    ctx.current_class_name = name
    ctx.current_base_class_name = base_name
    emitted_fields: set[str] = set()
    for field_name, field_type in _dict(node, "field_types").items():
        if isinstance(field_name, str) and isinstance(field_type, str):
            ctx.lines.append("    " * ctx.indent_level + "public " + _render_type(ctx, field_type) + " " + _safe_name(ctx, field_name) + ";")
            emitted_fields.add(_safe_name(ctx, field_name))
    for stmt in _list(node, "body"):
        if not isinstance(stmt, dict):
            continue
        kind = _str(stmt, "kind")
        if kind == "FunctionDef" or kind == "ClosureDef":
            _emit_function(ctx, stmt, force_public=True, static_method=False)
        elif kind == "AnnAssign":
            field_name = _emit_expr(ctx, stmt.get("target"))
            if field_name in emitted_fields:
                continue
            field_type = _target_type_from_stmt(ctx, stmt)
            value = stmt.get("value")
            init = cs_zero_value(_str(stmt, "decl_type"), mapping=ctx.mapping)
            if isinstance(value, dict):
                init = _render_expr_with_preferred_type(ctx, value, preferred_type=_str(stmt, "decl_type"))
            ctx.lines.append("    " * ctx.indent_level + "public " + field_type + " " + field_name + " = " + init + ";")
            emitted_fields.add(field_name)
        elif kind == "Assign":
            field_name2 = _emit_expr(ctx, stmt.get("target"))
            if field_name2 in emitted_fields:
                continue
            value2 = stmt.get("value")
            field_type2 = "object"
            init2 = "null"
            if isinstance(value2, dict):
                field_type2 = _render_type(ctx, _str(value2, "resolved_type"))
                init2 = _emit_expr(ctx, value2)
            ctx.lines.append("    " * ctx.indent_level + "public static " + field_type2 + " " + field_name2 + " = " + init2 + ";")
            emitted_fields.add(field_name2)
    ctx.current_class_name = previous_class
    ctx.current_base_class_name = previous_base_class
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")


def _emit_stmt_extension(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    kind = _str(node, "kind")
    indent = "    " * ctx.indent_level
    if kind == "FunctionDef":
        _emit_function(ctx, node)
        return
    if kind == "ClosureDef":
        _emit_function(ctx, node, force_public=False, static_method=False)
        return
    if kind == "ClassDef":
        _emit_class(ctx, node)
        return
    if kind == "ForRange":
        _emit_for_range(ctx, node)
        return
    if kind == "For":
        _emit_for_each(ctx, node)
        return
    if kind == "ForCore":
        _emit_for_core(ctx, node)
        return
    if kind == "AugAssign":
        _emit_aug_assign_stmt(ctx, node)
        return
    if kind == "Break":
        ctx.lines.append(indent + "break;")
        return
    if kind == "Continue":
        ctx.lines.append(indent + "continue;")
        return
    if kind == "Import" or kind == "ImportFrom":
        return
    ctx.lines.append(indent + "// unsupported stmt kind: " + kind)


def _emit_stmt_list(ctx: EmitContext, stmts: list[JsonVal]) -> None:
    renderer = _CsStmtCommonRenderer(ctx)
    renderer.state.lines = ctx.lines
    renderer.state.indent_level = ctx.indent_level
    for stmt in stmts:
        renderer.emit_stmt(stmt)
    ctx.indent_level = renderer.state.indent_level


def _emit_main_method(ctx: EmitContext, main_guard_body: list[JsonVal]) -> None:
    indent = "    " * ctx.indent_level
    ctx.lines.append(indent + "public static void Main(string[] args) {")
    ctx.indent_level += 1
    _emit_stmt_list(ctx, main_guard_body)
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")


def emit_cs_module(east3_doc: dict[str, JsonVal]) -> str:
    meta = _dict(east3_doc, "meta")
    module_id = ""
    emit_ctx_meta = _dict(meta, "emit_context")
    if len(emit_ctx_meta) > 0:
        module_id = _str(emit_ctx_meta, "module_id")
    if module_id == "":
        module_id = _str(meta, "module_id")
    lp = _dict(meta, "linked_program_v1")
    if module_id == "" and len(lp) > 0:
        module_id = _str(lp, "module_id")

    if module_id != "":
        expand_cross_module_defaults([(module_id, east3_doc)])

    mapping_path = Path(__file__).resolve().parents[3] / "runtime" / "cs" / "mapping.json"
    mapping = load_runtime_mapping(mapping_path)
    if should_skip_module(module_id, mapping):
        return ""

    renamed_symbols_raw = east3_doc.get("renamed_symbols")
    renamed_symbols: dict[str, str] = {}
    if isinstance(renamed_symbols_raw, dict):
        for key, value in renamed_symbols_raw.items():
            if isinstance(key, str) and isinstance(value, str):
                renamed_symbols[key] = value

    body = _list(east3_doc, "body")
    main_guard_body = _list(east3_doc, "main_guard_body")
    class_names: set[str] = set()
    class_bases: dict[str, str] = {}
    for stmt in body:
        if isinstance(stmt, dict) and _str(stmt, "kind") == "ClassDef":
            name = _str(stmt, "name")
            if name != "":
                class_names.add(name)
                base = _str(stmt, "base")
                if base != "":
                    class_bases[name] = base

    ctx = EmitContext(
        module_id=module_id,
        source_path=_str(east3_doc, "source_path"),
        is_entry=_bool(emit_ctx_meta, "is_entry") if len(emit_ctx_meta) > 0 else False,
        mapping=mapping,
        import_alias_modules=build_import_alias_map(meta),
        runtime_imports=build_runtime_import_map(meta, mapping),
        class_names=class_names,
        class_bases=class_bases,
        renamed_symbols=renamed_symbols,
    )
    class_name = _module_class_name(module_id)

    ctx.lines.append("using System;")
    ctx.lines.append("using System.Collections.Generic;")
    ctx.lines.append("")
    ctx.lines.append("namespace Pytra.CsModule")
    ctx.lines.append("{")
    ctx.indent_level = 1
    ctx.lines.append("    public static class " + class_name)
    ctx.lines.append("    {")
    ctx.indent_level = 2

    for stmt in body:
        if not isinstance(stmt, dict):
            continue
        kind = _str(stmt, "kind")
        if kind == "FunctionDef" or kind == "ClassDef":
            _emit_stmt_extension(ctx, stmt)
            continue
        if kind == "AnnAssign":
            target_name = _emit_expr(ctx, stmt.get("target"))
            decl_type = _target_type_from_stmt(ctx, stmt)
            value = stmt.get("value")
            init = cs_zero_value(_str(stmt, "decl_type"), mapping=ctx.mapping)
            if isinstance(value, dict):
                init = _emit_expr(ctx, value)
            ctx.lines.append("        public static " + decl_type + " " + target_name + " = " + init + ";")
            continue
        if kind == "Assign":
            target_name2 = _emit_expr(ctx, stmt.get("target"))
            value2 = stmt.get("value")
            init2 = _emit_expr(ctx, value2)
            target_type2 = "object"
            if isinstance(value2, dict):
                target_type2 = cs_type(_str(value2, "resolved_type"), mapping=ctx.mapping)
            ctx.lines.append("        public static " + target_type2 + " " + target_name2 + " = " + init2 + ";")

    if ctx.is_entry and len(main_guard_body) > 0:
        if len(body) > 0:
            ctx.lines.append("")
        _emit_main_method(ctx, main_guard_body)

    ctx.indent_level = 1
    ctx.lines.append("    }")
    ctx.lines.append("}")
    return "\n".join(ctx.lines).rstrip() + "\n"
