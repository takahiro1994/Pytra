"""Import map extraction from EAST3 meta.

§5 準拠: Any/object 禁止, pytra.std.* のみ, selfhost 対象。
ロジック参照元: toolchain/compile/east3_opt_passes/non_escape_call_graph.py (import はしない)。
"""

from __future__ import annotations

from pytra.std.json import JsonVal


def collect_import_maps(
    east_doc: dict[str, JsonVal],
) -> tuple[dict[str, str], dict[str, str]]:
    """Extract import_modules and import_symbols from EAST3 meta.

    Returns:
        (import_modules, import_symbols)
        - import_modules: {alias: module_id} for `import module [as alias]`
        - import_symbols: {alias: "module_id::export_name"} for `from module import name [as alias]`
    """
    import_modules: dict[str, str] = {}
    import_symbols: dict[str, str] = {}

    meta_val = east_doc.get("meta")
    if not isinstance(meta_val, dict):
        return import_modules, import_symbols

    # meta.import_modules: {alias: module_id}
    im_val = meta_val.get("import_modules")
    if isinstance(im_val, dict):
        for alias, mod_id in im_val.items():
            if isinstance(alias, str) and isinstance(mod_id, str):
                import_modules[alias] = mod_id

    # meta.import_symbols: {alias: {module: str, name: str}}
    is_val = meta_val.get("import_symbols")
    if isinstance(is_val, dict):
        for alias, info in is_val.items():
            if isinstance(alias, str) and isinstance(info, dict):
                mod = info.get("module")
                name = info.get("name")
                if isinstance(mod, str) and isinstance(name, str):
                    import_symbols[alias] = mod + "::" + name

    return import_modules, import_symbols
