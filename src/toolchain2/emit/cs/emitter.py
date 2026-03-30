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
    renamed_symbols: dict[str, str] = field(default_factory=dict)


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


def _quote_string(value: str) -> str:
    return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\""


def _target_type_from_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    for key in ("decl_type", "annotation", "resolved_type"):
        text = _str(node, key)
        if text != "":
            return cs_type(text, mapping=ctx.mapping)
    target = node.get("target")
    if isinstance(target, dict):
        rt = _str(target, "resolved_type")
        if rt != "":
            return cs_type(rt, mapping=ctx.mapping)
    return "object"


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


def _render_list_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elems = _list(node, "elements")
    rt = _str(node, "resolved_type")
    out_type = "List<object>"
    if rt != "":
        out_type = cs_type(rt, mapping=ctx.mapping)
    rendered = [_emit_expr(ctx, elem) for elem in elems]
    if len(rendered) == 0:
        return "new " + out_type + "()"
    return "new " + out_type + " { " + ", ".join(rendered) + " }"


def _render_set_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    elems = _list(node, "elements")
    rt = _str(node, "resolved_type")
    out_type = "HashSet<object>"
    if rt != "":
        out_type = cs_type(rt, mapping=ctx.mapping)
    rendered = [_emit_expr(ctx, elem) for elem in elems]
    if len(rendered) == 0:
        return "new " + out_type + "()"
    return "new " + out_type + " { " + ", ".join(rendered) + " }"


def _render_dict_literal(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    entries = _list(node, "entries")
    rt = _str(node, "resolved_type")
    out_type = "Dictionary<object, object>"
    if rt != "":
        out_type = cs_type(rt, mapping=ctx.mapping)
    rendered_entries: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        rendered_entries.append("{ " + _emit_expr(ctx, entry.get("key")) + ", " + _emit_expr(ctx, entry.get("value")) + " }")
    if len(rendered_entries) == 0:
        return "new " + out_type + "()"
    return "new " + out_type + " { " + ", ".join(rendered_entries) + " }"


def _render_subscript(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner = _emit_expr(ctx, node.get("value"))
    index = _emit_expr(ctx, node.get("slice"))
    return owner + "[" + index + "]"


def _render_ifexp(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    test = _emit_condition_expr(ctx, node.get("test"), wrap=False)
    body = _emit_expr(ctx, node.get("body"))
    orelse = _emit_expr(ctx, node.get("orelse"))
    return "(" + test + " ? " + body + " : " + orelse + ")"


def _emit_attribute(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    owner = _emit_expr(ctx, node.get("value"))
    attr = _safe_cs_ident(_str(node, "attr"))
    return owner + "." + attr


def _call_builtin_name(node: dict[str, JsonVal]) -> str:
    func = node.get("func")
    if isinstance(func, dict):
        kind = _str(func, "kind")
        if kind == "Name":
            return _str(func, "id")
        if kind == "Attribute":
            return _str(func, "attr")
    return ""


def _emit_call(ctx: EmitContext, node: dict[str, JsonVal]) -> str:
    args = [_emit_expr(ctx, arg) for arg in _list(node, "args")]
    runtime_call = _str(node, "runtime_call")
    builtin_name = _call_builtin_name(node)
    adapter = _str(node, "runtime_call_adapter_kind")
    resolved = resolve_runtime_call(runtime_call, builtin_name, adapter, ctx.mapping)
    if resolved == "__CAST__":
        if len(args) == 1:
            target_type = cs_type(_str(node, "resolved_type"), mapping=ctx.mapping)
            return "((" + target_type + ")" + args[0] + ")"
        return args[0] if len(args) > 0 else ""
    if resolved != "" and not resolved.startswith("__"):
        return resolved + "(" + ", ".join(args) + ")"
    func = node.get("func")
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
        return _emit_expr(self.ctx, node.get("exc"))

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
            return "Tuple.Create(" + ", ".join(items) + ")"
        return "/* unsupported:" + kind + " */"


def _emit_assign_stmt(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    target = node.get("target")
    value = node.get("value")
    target_text = _emit_expr(ctx, target)
    value_text = _emit_expr(ctx, value)
    declare = _bool(node, "declare") or _str(node, "kind") == "AnnAssign"
    if declare:
        decl_type = _target_type_from_stmt(ctx, node)
        ctx.var_types[target_text] = decl_type
        ctx.lines.append("    " * ctx.indent_level + decl_type + " " + target_text + " = " + value_text + ";")
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


def _emit_function(ctx: EmitContext, node: dict[str, JsonVal], *, force_public: bool = True, static_method: bool = True) -> None:
    name = _safe_name(ctx, _str(node, "name"))
    return_type = _str(node, "return_type")
    if return_type == "":
        return_type = "None"
    ctx.current_return_type = return_type
    args = _list(node, "args")
    arg_types = _dict(node, "arg_types")
    params: list[str] = []
    for arg in args:
        if not isinstance(arg, dict):
            continue
        arg_name = _safe_name(ctx, _str(arg, "arg"))
        src_type = ""
        if arg_name in arg_types and isinstance(arg_types[arg_name], str):
            src_type = str(arg_types[arg_name])
        if src_type == "":
            src_type = _str(arg, "resolved_type")
        if src_type == "":
            src_type = "object"
        params.append(cs_type(src_type, mapping=ctx.mapping) + " " + arg_name)
    modifiers: list[str] = []
    if force_public:
        modifiers.append("public")
    if static_method:
        modifiers.append("static")
    signature = " ".join(modifiers + [cs_type(return_type, mapping=ctx.mapping, for_return=True), name])
    indent = "    " * ctx.indent_level
    ctx.lines.append(indent + signature + "(" + ", ".join(params) + ") {")
    ctx.indent_level += 1
    _emit_stmt_list(ctx, _list(node, "body"))
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")


def _emit_class(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    name = _safe_name(ctx, _str(node, "name"))
    indent = "    " * ctx.indent_level
    ctx.lines.append(indent + "public sealed class " + name + " {")
    ctx.indent_level += 1
    previous_class = ctx.current_class_name
    ctx.current_class_name = name
    for stmt in _list(node, "body"):
        if not isinstance(stmt, dict):
            continue
        kind = _str(stmt, "kind")
        if kind == "FunctionDef":
            _emit_function(ctx, stmt, force_public=True, static_method=False)
        elif kind == "AnnAssign":
            field_name = _emit_expr(ctx, stmt.get("target"))
            field_type = _target_type_from_stmt(ctx, stmt)
            value = stmt.get("value")
            init = cs_zero_value(_str(stmt, "decl_type"), mapping=ctx.mapping)
            if isinstance(value, dict):
                init = _emit_expr(ctx, value)
            ctx.lines.append("    " * ctx.indent_level + "public " + field_type + " " + field_name + " = " + init + ";")
    ctx.current_class_name = previous_class
    ctx.indent_level -= 1
    ctx.lines.append(indent + "}")


def _emit_stmt_extension(ctx: EmitContext, node: dict[str, JsonVal]) -> None:
    kind = _str(node, "kind")
    indent = "    " * ctx.indent_level
    if kind == "FunctionDef":
        _emit_function(ctx, node)
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

    ctx = EmitContext(
        module_id=module_id,
        source_path=_str(east3_doc, "source_path"),
        is_entry=_bool(emit_ctx_meta, "is_entry") if len(emit_ctx_meta) > 0 else False,
        mapping=mapping,
        import_alias_modules=build_import_alias_map(meta),
        runtime_imports=build_runtime_import_map(meta, mapping),
        renamed_symbols=renamed_symbols,
    )

    body = _list(east3_doc, "body")
    main_guard_body = _list(east3_doc, "main_guard_body")
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
