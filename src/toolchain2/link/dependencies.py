"""Dependency table builder for linked programs.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
ロジック参照元: toolchain/link/global_optimizer.py _build_all_resolved_dependencies (import はしない)。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytra.std.json import JsonVal

if TYPE_CHECKING:
    from toolchain2.link.linker import LinkedModule


def _build_resolved_dependencies(
    east_doc: dict[str, JsonVal],
) -> list[str]:
    """Build resolved dependency list for a single module from its EAST3 meta."""
    deps: list[str] = []
    seen: set[str] = set()

    meta_val = east_doc.get("meta")
    if not isinstance(meta_val, dict):
        return deps

    # From import_bindings
    bindings = meta_val.get("import_bindings")
    if isinstance(bindings, list):
        for binding in bindings:
            if not isinstance(binding, dict):
                continue
            mod_id = binding.get("module_id")
            if isinstance(mod_id, str) and mod_id.strip() != "" and mod_id not in seen:
                seen.add(mod_id)
                deps.append(mod_id)

    # From body Import/ImportFrom
    body_val = east_doc.get("body")
    if isinstance(body_val, list):
        for stmt in body_val:
            if not isinstance(stmt, dict):
                continue
            kind = stmt.get("kind")
            if kind == "ImportFrom":
                mod = stmt.get("module")
                if isinstance(mod, str) and mod.strip() != "" and mod not in seen:
                    seen.add(mod)
                    deps.append(mod)
            elif kind == "Import":
                names = stmt.get("names")
                if isinstance(names, list):
                    for ent in names:
                        if isinstance(ent, dict):
                            name = ent.get("name")
                            if isinstance(name, str) and name.strip() != "" and name not in seen:
                                seen.add(name)
                                deps.append(name)

    return sorted(deps)


def build_all_resolved_dependencies(
    modules: list[LinkedModule],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Build resolved_dependencies_v1 and user_module_dependencies_v1 for all modules.

    Returns:
        (resolved_deps_by_module, user_deps_by_module)
    """
    # Collect all user module IDs
    user_module_ids: set[str] = set()
    for module in modules:
        if module.module_kind == "user":
            user_module_ids.add(module.module_id)

    resolved: dict[str, list[str]] = {}
    user_deps: dict[str, list[str]] = {}

    for module in modules:
        doc = module.east_doc
        if not isinstance(doc, dict):
            resolved[module.module_id] = []
            user_deps[module.module_id] = []
            continue

        deps = _build_resolved_dependencies(doc)
        resolved[module.module_id] = deps
        # Filter to only user module dependencies (exclude self)
        u_deps = [d for d in deps if d in user_module_ids and d != module.module_id]
        user_deps[module.module_id] = u_deps

    return resolved, user_deps
