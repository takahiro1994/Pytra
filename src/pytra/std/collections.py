"""Pytra collections module — re-exports from Python standard collections.

Python runtime: standard collections (deque etc.) are available.
Transpiler: ignores this import (deque is recognized natively as a builtin type).
"""

from collections import deque

__all__ = ["deque"]
