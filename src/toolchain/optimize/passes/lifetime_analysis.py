"""Function-local lifetime analysis for EAST3 (CFG + def-use + liveness)."""

from __future__ import annotations

from dataclasses import dataclass

from pytra.std.json import JsonVal

from toolchain.optimize.optimizer import East3OptimizerPass, PassContext, PassResult, make_pass_result


_DYNAMIC_NAME_CALLS: set[str] = {"locals", "globals", "vars", "eval", "exec"}
_LOOP_KINDS: set[str] = {"For", "ForRange", "ForCore", "While"}


def _safe_name(value: JsonVal) -> str:
    if isinstance(value, str):
        text = value.strip()
        if text != "":
            return text
    return ""


def _ensure_meta(node: dict[str, JsonVal]) -> dict[str, JsonVal]:
    meta_val = node.get("meta")
    if isinstance(meta_val, dict):
        return meta_val
    meta: dict[str, JsonVal] = {}
    node["meta"] = meta
    return meta


def _set_meta_value(node: dict[str, JsonVal], key: str, value: JsonVal) -> bool:
    meta = _ensure_meta(node)
    if meta.get(key) == value:
        return False
    meta[key] = value
    return True


def _iter_stmt_list(value: JsonVal) -> list[dict[str, JsonVal]]:
    src = value if isinstance(value, list) else []
    out: list[dict[str, JsonVal]] = []
    for item in src:
        if isinstance(item, dict):
            out.append(item)
    return out


def _collect_target_defs(node: JsonVal, out: set[str]) -> None:
    if not isinstance(node, dict):
        return
    kind = _safe_name(node.get("kind"))
    if kind == "Name":
        ident = _safe_name(node.get("id"))
        if ident != "":
            out.add(ident)
        return
    if kind == "Tuple" or kind == "List":
        elements_val = node.get("elements")
        elements = elements_val if isinstance(elements_val, list) else []
        for elem in elements:
            _collect_target_defs(elem, out)


def _collect_target_plan_defs(node: JsonVal, out: set[str]) -> None:
    if not isinstance(node, dict):
        return
    kind = _safe_name(node.get("kind"))
    if kind == "NameTarget":
        ident = _safe_name(node.get("id"))
        if ident != "":
            out.add(ident)
        return
    if kind == "TupleTarget":
        elements_val = node.get("elements")
        elements = elements_val if isinstance(elements_val, list) else []
        for elem in elements:
            _collect_target_plan_defs(elem, out)


def _collect_name_uses(node: JsonVal, out: set[str]) -> None:
    if isinstance(node, list):
        for item in node:
            _collect_name_uses(item, out)
        return
    if not isinstance(node, dict):
        return
    kind = _safe_name(node.get("kind"))
    if kind == "Name":
        ident = _safe_name(node.get("id"))
        if ident != "":
            out.add(ident)
        return
    for value in node.values():
        _collect_name_uses(value, out)


def _has_dynamic_name_access(node: JsonVal) -> bool:
    if isinstance(node, list):
        for item in node:
            if _has_dynamic_name_access(item):
                return True
        return False
    if not isinstance(node, dict):
        return False
    kind = _safe_name(node.get("kind"))
    if kind == "Call":
        func_val = node.get("func")
        if isinstance(func_val, dict) and _safe_name(func_val.get("kind")) == "Name":
            fn_name = _safe_name(func_val.get("id"))
            if fn_name in _DYNAMIC_NAME_CALLS:
                return True
    for value in node.values():
        if _has_dynamic_name_access(value):
            return True
    return False


def _stmt_defs_uses(stmt: dict[str, JsonVal]) -> tuple[set[str], set[str], bool]:
    defs: set[str] = set()
    uses: set[str] = set()
    kind = _safe_name(stmt.get("kind"))

    if kind == "Assign":
        _collect_target_defs(stmt.get("target"), defs)
        _collect_name_uses(stmt.get("value"), uses)
    elif kind == "AnnAssign":
        _collect_target_defs(stmt.get("target"), defs)
        _collect_name_uses(stmt.get("value"), uses)
    elif kind == "AugAssign":
        _collect_target_defs(stmt.get("target"), defs)
        _collect_name_uses(stmt.get("target"), uses)
        _collect_name_uses(stmt.get("value"), uses)
    elif kind == "Expr":
        _collect_name_uses(stmt.get("value"), uses)
    elif kind == "Return" or kind == "Yield":
        _collect_name_uses(stmt.get("value"), uses)
    elif kind == "If":
        _collect_name_uses(stmt.get("test"), uses)
    elif kind == "While":
        _collect_name_uses(stmt.get("test"), uses)
    elif kind == "For":
        _collect_target_defs(stmt.get("target"), defs)
        _collect_name_uses(stmt.get("iter"), uses)
    elif kind == "ForRange":
        _collect_target_defs(stmt.get("target"), defs)
        _collect_name_uses(stmt.get("start"), uses)
        _collect_name_uses(stmt.get("stop"), uses)
        _collect_name_uses(stmt.get("step"), uses)
    elif kind == "ForCore":
        _collect_target_plan_defs(stmt.get("target_plan"), defs)
        _collect_name_uses(stmt.get("iter_plan"), uses)
        _collect_name_uses(stmt.get("iter"), uses)
    elif kind == "FunctionDef" or kind == "ClosureDef":
        name = _safe_name(stmt.get("name"))
        if name != "":
            defs.add(name)
    elif kind == "ClassDef":
        name = _safe_name(stmt.get("name"))
        if name != "":
            defs.add(name)
    elif kind == "With":
        _collect_name_uses(stmt.get("items"), uses)
    elif kind == "Try":
        _collect_name_uses(stmt.get("handlers"), uses)
    else:
        _collect_name_uses(stmt, uses)

    return defs, uses, _has_dynamic_name_access(stmt)


def _function_args(fn_node: dict[str, JsonVal]) -> list[str]:
    out: list[str] = []
    arg_order_val = fn_node.get("arg_order")
    if isinstance(arg_order_val, list):
        for item in arg_order_val:
            name = _safe_name(item)
            if name != "":
                out.append(name)
        return out
    args_val = fn_node.get("args")
    args = args_val if isinstance(args_val, list) else []
    for arg_item in args:
        if not isinstance(arg_item, dict):
            continue
        name = _safe_name(arg_item.get("arg"))
        if name == "":
            name = _safe_name(arg_item.get("id"))
        if name != "":
            out.append(name)
    return out


@dataclass
class CfgNode:
    node_id: str
    stmt: dict[str, JsonVal]
    kind: str
    defs: set[str]
    uses: set[str]
    succ: set[str]


class CfgBuilder:
    def __init__(self) -> None:
        self._counter: int = 0
        self.nodes: dict[str, CfgNode] = {}
        self.order: list[str] = []
        self.dynamic_name_access: bool = False

    def _new_node(self, stmt: dict[str, JsonVal]) -> CfgNode:
        node_id = "n" + str(self._counter)
        self._counter += 1
        defs, uses, has_dyn = _stmt_defs_uses(stmt)
        if has_dyn:
            self.dynamic_name_access = True
        node = CfgNode(
            node_id=node_id,
            stmt=stmt,
            kind=_safe_name(stmt.get("kind")),
            defs=set(defs),
            uses=set(uses),
            succ=_empty_str_set(),
        )
        self.nodes[node_id] = node
        self.order.append(node_id)
        return node

    def build_block(
        self,
        stmts: list[dict[str, JsonVal]],
        next_node: str,
        loop_ctx: tuple[str, str] | None,
    ) -> str:
        entry = next_node
        for stmt in reversed(stmts):
            entry = self.build_stmt(stmt, entry, loop_ctx)
        return entry

    def build_stmt(
        self,
        stmt: dict[str, JsonVal],
        next_node: str,
        loop_ctx: tuple[str, str] | None,
    ) -> str:
        node = self._new_node(stmt)
        kind = node.kind

        if kind == "Return" or kind == "Yield":
            return node.node_id

        if kind == "Break":
            if loop_ctx is not None and loop_ctx[1] != "":
                node.succ.add(loop_ctx[1])
            elif next_node != "":
                node.succ.add(next_node)
            return node.node_id

        if kind == "Continue":
            if loop_ctx is not None and loop_ctx[0] != "":
                node.succ.add(loop_ctx[0])
            elif next_node != "":
                node.succ.add(next_node)
            return node.node_id

        if kind == "If":
            body = _iter_stmt_list(stmt.get("body"))
            orelse = _iter_stmt_list(stmt.get("orelse"))
            body_entry = self.build_block(body, next_node, loop_ctx)
            orelse_entry = self.build_block(orelse, next_node, loop_ctx)
            if body_entry != "":
                node.succ.add(body_entry)
            elif next_node != "":
                node.succ.add(next_node)
            if orelse_entry != "":
                node.succ.add(orelse_entry)
            elif next_node != "":
                node.succ.add(next_node)
            return node.node_id

        if kind in _LOOP_KINDS:
            body = _iter_stmt_list(stmt.get("body"))
            orelse = _iter_stmt_list(stmt.get("orelse"))
            orelse_entry = self.build_block(orelse, next_node, loop_ctx)
            exit_target = orelse_entry if orelse_entry != "" else next_node
            body_entry = self.build_block(body, node.node_id, (node.node_id, exit_target))
            if body_entry != "":
                node.succ.add(body_entry)
            else:
                node.succ.add(node.node_id)
            if exit_target != "":
                node.succ.add(exit_target)
            return node.node_id

        if next_node != "":
            node.succ.add(next_node)
        return node.node_id


def _sorted_str_list(values: set[str]) -> list[str]:
    return sorted(values)


def _sorted_set_map(values: dict[str, set[str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for name in sorted(values.keys()):
        out[name] = _sorted_str_list(values[name])
    return out


def _merge_set_map(dst: dict[str, set[str]], key: str, values: set[str]) -> None:
    if key not in dst:
        dst[key] = _empty_str_set()
    dst[key].update(values)


def _empty_str_set() -> set[str]:
    out: set[str] = set()
    return out


def _set_minus(left: set[str], right: set[str]) -> set[str]:
    out: set[str] = _empty_str_set()
    for value in left:
        if value not in right:
            out.add(value)
    return out


def _policy_flag(context: PassContext, key: str, default: bool) -> bool:
    if key in context.non_escape_policy:
        return bool(context.non_escape_policy[key])
    return default


def _sets_equal(left: set[str], right: set[str]) -> bool:
    if len(left) != len(right):
        return False
    for value in left:
        if value not in right:
            return False
    return True


def _compute_liveness(nodes: dict[str, CfgNode], order: list[str]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    live_in: dict[str, set[str]] = {node_id: _empty_str_set() for node_id in order}
    live_out: dict[str, set[str]] = {node_id: _empty_str_set() for node_id in order}
    changed = True
    while changed:
        changed = False
        for node_id in reversed(order):
            node = nodes[node_id]
            out_set: set[str] = _empty_str_set()
            for succ in node.succ:
                if succ in live_in:
                    out_set.update(live_in[succ])
            in_set = set(node.uses)
            in_set.update(_set_minus(out_set, node.defs))
            prev_out = live_out[node_id] if node_id in live_out else _empty_str_set()
            prev_in = live_in[node_id] if node_id in live_in else _empty_str_set()
            if (not _sets_equal(out_set, prev_out)) or (not _sets_equal(in_set, prev_in)):
                live_out[node_id] = out_set
                live_in[node_id] = in_set
                changed = True
    return live_in, live_out


def _non_escape_arg_flags(fn_node: dict[str, JsonVal], context: PassContext) -> list[bool]:
    arg_names = _function_args(fn_node)
    defaults = [_policy_flag(context, "return_escape_by_default", True)] * len(arg_names)
    meta_val = fn_node.get("meta")
    meta = meta_val if isinstance(meta_val, dict) else {}
    summary_val = meta.get("escape_summary")
    summary = summary_val if isinstance(summary_val, dict) else {}
    flags_val = summary.get("arg_escape")
    flags = flags_val if isinstance(flags_val, list) else []
    if len(flags) == 0:
        return defaults
    out = list(defaults)
    for i, flag_item in enumerate(flags):
        if i >= len(out):
            break
        if isinstance(flag_item, bool):
            out[i] = bool(flag_item)
    return out


class LifetimeAnalysisPass(East3OptimizerPass):
    """Attach deterministic function-local lifetime metadata (east3_lifetime_v1)."""

    name: str = "LifetimeAnalysisPass"
    min_opt_level: int = 1

    def _analyze_function(self, fn_node: dict[str, JsonVal], context: PassContext) -> bool:
        body = _iter_stmt_list(fn_node.get("body"))
        builder = CfgBuilder()
        entry_id = builder.build_block(body, "", None)
        order = list(builder.order)
        nodes = builder.nodes

        defs_index: dict[str, set[str]] = {}
        uses_index: dict[str, set[str]] = {}
        return_use_index: dict[str, set[str]] = {}

        for node_id in order:
            node = nodes[node_id]
            for name in node.defs:
                _merge_set_map(defs_index, name, {node_id})
            for name in node.uses:
                _merge_set_map(uses_index, name, {node_id})
            if node.kind == "Return" or node.kind == "Yield":
                for name in node.uses:
                    _merge_set_map(return_use_index, name, {node_id})

        live_in, live_out = _compute_liveness(nodes, order)
        args = _function_args(fn_node)
        arg_escape = _non_escape_arg_flags(fn_node, context)

        all_vars: set[str] = set(args)
        all_vars.update(defs_index.keys())
        all_vars.update(uses_index.keys())

        variables: dict[str, JsonVal] = {}
        fail_closed = bool(builder.dynamic_name_access)
        for name in sorted(all_vars):
            def_nodes = _sorted_str_list(defs_index.get(name, _empty_str_set()))
            use_nodes = _sorted_str_list(uses_index.get(name, _empty_str_set()))
            live_in_nodes = [node_id for node_id in order if name in live_in.get(node_id, set())]
            live_out_nodes = [node_id for node_id in order if name in live_out.get(node_id, set())]
            last_use_nodes: list[str] = []
            for node_id in use_nodes:
                if name not in live_out.get(node_id, set()):
                    last_use_nodes.append(node_id)
            lifetime_class = "local_non_escape_candidate"
            if fail_closed:
                lifetime_class = "escape_or_unknown"
            if name in return_use_index:
                lifetime_class = "escape_or_unknown"
            if name in args:
                arg_index = args.index(name)
                if arg_index < len(arg_escape) and bool(arg_escape[arg_index]):
                    lifetime_class = "escape_or_unknown"
            var_info: dict[str, JsonVal] = {}
            var_info["def_nodes"] = def_nodes
            var_info["use_nodes"] = use_nodes
            var_info["live_in_nodes"] = live_in_nodes
            var_info["live_out_nodes"] = live_out_nodes
            var_info["last_use_nodes"] = sorted(last_use_nodes)
            var_info["lifetime_class"] = lifetime_class
            variables[name] = var_info

        changed = False
        for node_id in order:
            node = nodes[node_id]
            last_use_vars = [name for name in sorted(node.uses) if name not in live_out.get(node_id, set())]
            if _set_meta_value(node.stmt, "lifetime_node_id", node_id):
                changed = True
            if _set_meta_value(node.stmt, "lifetime_defs", sorted(node.defs)):
                changed = True
            if _set_meta_value(node.stmt, "lifetime_uses", sorted(node.uses)):
                changed = True
            if _set_meta_value(node.stmt, "lifetime_live_in", _sorted_str_list(live_in.get(node_id, set()))):
                changed = True
            if _set_meta_value(node.stmt, "lifetime_live_out", _sorted_str_list(live_out.get(node_id, set()))):
                changed = True
            if _set_meta_value(node.stmt, "lifetime_last_use_vars", last_use_vars):
                changed = True

        node_summaries: list[JsonVal] = []
        for node_id in order:
            node = nodes[node_id]
            node_summary: dict[str, JsonVal] = {}
            node_summary["id"] = node_id
            node_summary["kind"] = node.kind
            node_summary["defs"] = sorted(node.defs)
            node_summary["uses"] = sorted(node.uses)
            node_summary["succ"] = sorted(node.succ)
            node_summaries.append(node_summary)

        fn_analysis: dict[str, JsonVal] = {
            "schema_version": "east3_lifetime_v1",
            "status": "fail_closed" if fail_closed else "ok",
            "reason": "dynamic_name_access" if fail_closed else "",
            "entry_node": entry_id,
            "order": list(order),
            "cfg": node_summaries,
            "def_use": {
                "defs": _sorted_set_map(defs_index),
                "uses": _sorted_set_map(uses_index),
            },
            "variables": variables,
            "arg_order": list(args),
            "arg_escape": [bool(v) for v in arg_escape],
            "has_dynamic_name_access": fail_closed,
        }
        if _set_meta_value(fn_node, "lifetime_analysis", fn_analysis):
            changed = True
        return changed

    def _visit(self, node: JsonVal, context: PassContext) -> int:
        if isinstance(node, list):
            changed = 0
            for item in node:
                changed += self._visit(item, context)
            return changed
        if not isinstance(node, dict):
            return 0

        kind = _safe_name(node.get("kind"))
        changed = 0
        if kind == "FunctionDef" or kind == "ClosureDef":
            if self._analyze_function(node, context):
                changed += 1
            return changed
        if kind == "ClassDef":
            body = _iter_stmt_list(node.get("body"))
            for item in body:
                if _safe_name(item.get("kind")) != "FunctionDef":
                    continue
                if self._analyze_function(item, context):
                    changed += 1
            return changed

        for value in node.values():
            changed += self._visit(value, context)
        return changed

    def run(self, east3_doc: dict[str, JsonVal], context: PassContext) -> PassResult:
        change_count = self._visit(east3_doc, context)
        if _set_meta_value(east3_doc, "lifetime_schema_version", "east3_lifetime_v1"):
            change_count += 1
        warnings: list[str] = []
        return make_pass_result(change_count > 0, change_count, warnings, 0.0)
