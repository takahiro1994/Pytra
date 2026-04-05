"""Default EAST3 optimizer pass registrations for toolchain."""

from __future__ import annotations

from toolchain.optimize.passes.noop_cast_cleanup import NoOpCastCleanupPass
from toolchain.optimize.passes.literal_cast_fold import LiteralCastFoldPass
from toolchain.optimize.passes.in_literal_expansion import InLiteralExpansionPass
from toolchain.optimize.passes.identity_py_to_elision import IdentityPyToElisionPass
from toolchain.optimize.passes.numeric_cast_chain_reduction import NumericCastChainReductionPass
from toolchain.optimize.passes.range_for_canonicalization import RangeForCanonicalizationPass
from toolchain.optimize.passes.expression_normalization import ExpressionNormalizationPass
from toolchain.optimize.passes.empty_init_shorthand import EmptyInitShorthandPass
from toolchain.optimize.passes.safe_reserve_hint import SafeReserveHintPass
from toolchain.optimize.passes.typed_enumerate_normalization import TypedEnumerateNormalizationPass
from toolchain.optimize.passes.typed_repeat_materialization import TypedRepeatMaterializationPass
from toolchain.optimize.passes.dict_str_key_normalization import DictStrKeyNormalizationPass
from toolchain.optimize.passes.tuple_target_direct_expansion import TupleTargetDirectExpansionPass
from toolchain.optimize.passes.lifetime_analysis import LifetimeAnalysisPass
from toolchain.optimize.passes.unused_loop_var_elision import UnusedLoopVarElisionPass
from toolchain.optimize.passes.strength_reduction_float_loop import StrengthReductionFloatLoopPass
from toolchain.optimize.passes.subscript_access_annotation import SubscriptAccessAnnotationPass
from toolchain.optimize.passes.pod_isinstance_fold import PodIsinstanceFoldPass

from toolchain.optimize.optimizer import East3OptimizerPass


def build_local_only_passes() -> list[East3OptimizerPass]:
    """Default local optimizer pass list."""
    return [
        NoOpCastCleanupPass(),
        LiteralCastFoldPass(),
        PodIsinstanceFoldPass(),
        InLiteralExpansionPass(),
        IdentityPyToElisionPass(),
        NumericCastChainReductionPass(),
        RangeForCanonicalizationPass(),
        ExpressionNormalizationPass(),
        EmptyInitShorthandPass(),
        SafeReserveHintPass(),
        TypedEnumerateNormalizationPass(),
        TypedRepeatMaterializationPass(),
        DictStrKeyNormalizationPass(),
        TupleTargetDirectExpansionPass(),
        LifetimeAnalysisPass(),
        UnusedLoopVarElisionPass(),
        StrengthReductionFloatLoopPass(),
        SubscriptAccessAnnotationPass(),
    ]


def build_default_passes() -> list[East3OptimizerPass]:
    """Backward-compatible default local pass list."""
    return build_local_only_passes()
