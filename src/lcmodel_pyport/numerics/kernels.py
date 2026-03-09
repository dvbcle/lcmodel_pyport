"""Compatibility re-exports for earlier numerics import paths."""

from __future__ import annotations

from lcmodel_pyport.fit.regularization import (
    count_inflections_extrema,
    regula_falsi,
    second_difference_regularization,
)
from lcmodel_pyport.fit.snapshots import Snapshot, restore_snapshot, save_snapshot
from lcmodel_pyport.fit.solver_linear import solve_nonnegative
from lcmodel_pyport.preprocess.fft_ops import cfft_r, cfftin_r, frequency_reindex
from lcmodel_pyport.preprocess.shift_phase import (
    apply_first_order_phase,
    apply_zero_order_phase,
    integer_shift_phase_ramp,
)
from lcmodel_pyport.report.diagnostics import covariance_uncertainty

__all__ = [
    "frequency_reindex",
    "cfft_r",
    "cfftin_r",
    "integer_shift_phase_ramp",
    "apply_zero_order_phase",
    "apply_first_order_phase",
    "solve_nonnegative",
    "regula_falsi",
    "second_difference_regularization",
    "count_inflections_extrema",
    "Snapshot",
    "save_snapshot",
    "restore_snapshot",
    "covariance_uncertainty",
]
