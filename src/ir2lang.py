#!/usr/bin/env python3
"""Compatibility shim — delegates to east2x.py.

Canonical entry point is now ``east2x.py``.
"""

from __future__ import annotations

import sys

import east2x

if __name__ == "__main__":
    sys.exit(east2x.main())
else:
    # Allow ``import ir2lang; ir2lang.main()`` for existing callers.
    main = east2x.main
