"""Re-export shared utilities from toolchain2/common/ (互換維持).

optimize/passes/ が toolchain.optimize.utils から import していた名前を
toolchain.common.* から re-export する。
"""

from __future__ import annotations

# jv
from toolchain.common.jv import deep_copy_json

# types
from toolchain.common.types import normalize_type_name
from toolchain.common.types import is_any_like_type
from toolchain.common.types import split_generic_types

# nodes
from toolchain.common.nodes import const_int_node
from toolchain.common.nodes import const_int_value
from toolchain.common.nodes import binop_expr
from toolchain.common.nodes import compare_expr
from toolchain.common.nodes import ifexp_expr

__all__ = [
    "deep_copy_json",
    "normalize_type_name",
    "is_any_like_type",
    "split_generic_types",
    "const_int_node",
    "const_int_value",
    "binop_expr",
    "compare_expr",
    "ifexp_expr",
]
