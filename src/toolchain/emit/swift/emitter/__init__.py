"""Swift emitter helpers (native only)."""

from __future__ import annotations

from typing import Any

from toolchain.emit.js.emitter.js_emitter import load_js_profile

from .swift_native_emitter import transpile_to_swift_native


def load_swift_profile() -> dict[str, Any]:
    """Swift backend で利用する profile を返す。"""
    return load_js_profile()


def transpile_to_swift(east_doc: dict[str, Any], js_entry_path: str = "program.js") -> str:
    """互換 API: native emitter へ委譲する。"""
    _ = js_entry_path
    # Skip built_in modules — they are covered by py_runtime.swift
    meta = east_doc.get("meta", {}) if isinstance(east_doc, dict) else {}
    emit_ctx = meta.get("emit_context", {}) if isinstance(meta, dict) else {}
    module_id = emit_ctx.get("module_id", "") if isinstance(emit_ctx, dict) else ""
    # built_in modules are covered by py_runtime.swift.
    # utils modules are also skipped: Swift [Any] is a value type so EAST3-generated
    # utils code (which uses pass-by-reference container mutation) does not work.
    # Image functions are provided by hand-written stubs in py_runtime.swift.
    # This will be resolved when §10 container reference semantics (class PyList) is implemented.
    if isinstance(module_id, str) and (module_id.startswith("pytra.built_in.") or module_id.startswith("pytra.utils.")):
        return ""
    return transpile_to_swift_native(east_doc)


__all__ = ["load_swift_profile", "transpile_to_swift", "transpile_to_swift_native"]
