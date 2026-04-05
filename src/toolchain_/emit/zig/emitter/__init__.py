"""Zig emitter helpers (native only)."""

from __future__ import annotations

from typing import Any

from toolchain.emit.js.emitter.js_emitter import load_js_profile

from .zig_native_emitter import transpile_to_zig_native


def load_zig_profile() -> dict[str, Any]:
    """Zig backend 用 profile を返す。"""
    return load_js_profile()


def transpile_to_zig(east_doc: dict[str, Any], js_entry_path: str = "program.js") -> str:
    """互換 API: native emitter へ委譲する。"""
    _ = js_entry_path
    return transpile_to_zig_native(east_doc)


__all__ = ["load_zig_profile", "transpile_to_zig", "transpile_to_zig_native"]
