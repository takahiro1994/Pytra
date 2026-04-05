"""Julia emitter helpers (native only)."""

from __future__ import annotations

from typing import Any

from .julia_native_emitter import transpile_to_julia_native


def transpile_to_julia(east_doc: dict[str, Any]) -> str:
    """互換 API: native emitter へ委譲する。"""
    return transpile_to_julia_native(east_doc)


__all__ = ["transpile_to_julia", "transpile_to_julia_native"]
