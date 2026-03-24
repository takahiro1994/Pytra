"""type_id table builder for linked programs.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
ロジック参照元: toolchain/link/global_optimizer.py _build_type_id_table (import はしない)。

割り当て規則 (spec-linker.md §6):
- built-in: 固定値 (NONE=0, OBJECT=8 等)
- user class: USER_BASE (1000) 以上を DFS で割り当て
- 決定性: 同一入力では常に同一 type_id
- 順序: 継承トポロジカル順 → 同順位は FQCN 辞書順
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytra.std.json import JsonVal

if TYPE_CHECKING:
    from toolchain2.link.linker import LinkedModule

from toolchain2.link.import_maps import collect_import_maps


_BUILTIN_TYPE_IDS: dict[str, int] = {
    "None": 0,
    "bool": 1,
    "int": 2,
    "float": 3,
    "str": 4,
    "list": 5,
    "dict": 6,
    "set": 7,
    "object": 8,
}

_ROOT_BASE_NAMES: set[str] = set(_BUILTIN_TYPE_IDS.keys()) | {
    "Enum",
    "IntEnum",
    "IntFlag",
    "BaseException",
    "Exception",
    "RuntimeError",
    "ValueError",
    "TypeError",
    "IndexError",
    "KeyError",
    "TypedDict",
}

_USER_TYPE_ID_BASE = 1000


def _safe_name(val: JsonVal) -> str:
    if isinstance(val, str):
        text = val.strip()
        if text != "":
            return text
    return ""


def _iter_class_defs(east_doc: dict[str, JsonVal]) -> list[dict[str, JsonVal]]:
    """Extract top-level ClassDef nodes from module body."""
    body_val = east_doc.get("body")
    body = body_val if isinstance(body_val, list) else []
    out: list[dict[str, JsonVal]] = []
    for item in body:
        if isinstance(item, dict) and item.get("kind") == "ClassDef":
            out.append(item)
    return out


def _resolve_class_base_fqcn(
    base_name: str,
    *,
    module_id: str,
    local_classes: dict[str, str],
    import_modules: dict[str, str],
    import_symbols: dict[str, str],
) -> str:
    """Resolve a base class name to a fully-qualified class name (FQCN)."""
    name = base_name.strip()
    if name == "":
        return "object"
    if name in _ROOT_BASE_NAMES:
        return name
    if name in local_classes:
        return local_classes[name]
    # Check import symbols (binding_kind=symbol: "module_id::export_name")
    imported_symbol = import_symbols.get(name, "").strip()
    if imported_symbol != "" and "::" in imported_symbol:
        dep_module_id, export_name = imported_symbol.split("::", 1)
        export_name = export_name.strip()
        if dep_module_id.strip() != "" and export_name != "":
            return dep_module_id.strip() + "." + export_name
    # Check dotted name (e.g. module.ClassName)
    if "." in name:
        owner_name, attr_name = name.split(".", 1)
        imported_module = import_modules.get(owner_name, "").strip()
        if imported_module != "" and attr_name.strip() != "":
            return imported_module + "." + attr_name.strip()
    # Fallback: assume local
    fqcn_candidate = module_id + "." + name
    if fqcn_candidate in local_classes.values():
        return fqcn_candidate
    return "object"


def build_type_id_table(
    modules: list[LinkedModule],
) -> tuple[dict[str, JsonVal], dict[str, JsonVal], dict[str, JsonVal]]:
    """Build type_id table, base_map, and info_table via DFS.

    Returns:
        (type_id_table, type_id_base_map, type_info_table)
        - type_id_table: {FQCN: int}
        - type_id_base_map: {FQCN: int}
        - type_info_table: {FQCN: {id, entry, exit}}
    """
    class_bases: dict[str, str] = {}
    children: dict[str, list[str]] = {}

    for module in sorted(modules, key=lambda m: m.module_id):
        doc = module.east_doc
        if not isinstance(doc, dict):
            continue

        import_modules, import_symbols = collect_import_maps(doc)

        # First pass: collect local class names → FQCN
        local_classes: dict[str, str] = {}
        class_defs = _iter_class_defs(doc)
        for class_def in class_defs:
            class_name = _safe_name(class_def.get("name"))
            if class_name == "":
                continue
            fqcn = module.module_id + "." + class_name
            local_classes[class_name] = fqcn

        # Second pass: resolve base classes
        for class_def in class_defs:
            class_name = _safe_name(class_def.get("name"))
            if class_name == "":
                continue
            fqcn = module.module_id + "." + class_name
            base_fqcn = _resolve_class_base_fqcn(
                _safe_name(class_def.get("base")),
                module_id=module.module_id,
                local_classes=local_classes,
                import_modules=import_modules,
                import_symbols=import_symbols,
            )
            class_bases[fqcn] = base_fqcn
            if fqcn not in children:
                children[fqcn] = []

    # Build children map
    for fqcn, base_fqcn in sorted(class_bases.items()):
        if base_fqcn in class_bases:
            if base_fqcn not in children:
                children[base_fqcn] = []
            children[base_fqcn].append(fqcn)

    # Sort children for determinism
    for parent in list(children.keys()):
        children[parent] = sorted(children[parent])

    # Find roots (classes whose base is not in class_bases)
    roots: list[str] = []
    for fqcn, base_fqcn in sorted(class_bases.items()):
        if base_fqcn not in class_bases:
            roots.append(fqcn)

    # DFS assignment
    next_id_holder: list[int] = [_USER_TYPE_ID_BASE]
    type_id_table: dict[str, int] = {}
    type_info_table: dict[str, dict[str, int]] = {}

    def _assign(fqcn: str) -> None:
        entry = next_id_holder[0]
        type_id_table[fqcn] = entry
        next_id_holder[0] = next_id_holder[0] + 1
        for child_fqcn in children.get(fqcn, []):
            _assign(child_fqcn)
        exit_val = next_id_holder[0]
        type_info_table[fqcn] = {"id": entry, "entry": entry, "exit": exit_val}

    for fqcn in sorted(roots):
        _assign(fqcn)

    # Build base type_id map
    type_id_base_map: dict[str, int] = {}
    for fqcn, base_fqcn in class_bases.items():
        if base_fqcn in type_id_table:
            type_id_base_map[fqcn] = type_id_table[base_fqcn]
        else:
            base_short = base_fqcn.rsplit(".", 1)[-1] if "." in base_fqcn else base_fqcn
            type_id_base_map[fqcn] = _BUILTIN_TYPE_IDS.get(base_short, _BUILTIN_TYPE_IDS["object"])

    # Convert to JsonVal-compatible dicts
    tid_table: dict[str, JsonVal] = {}
    for k, v in sorted(type_id_table.items()):
        tid_table[k] = v

    tid_base: dict[str, JsonVal] = {}
    for k, v in sorted(type_id_base_map.items()):
        tid_base[k] = v

    tid_info: dict[str, JsonVal] = {}
    for k, v in sorted(type_info_table.items()):
        info: dict[str, JsonVal] = {"id": v["id"], "entry": v["entry"], "exit": v["exit"]}
        tid_info[k] = info

    return tid_table, tid_base, tid_info
