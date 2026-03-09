from __future__ import annotations

import numpy as np
import pytest

from lcmodel_pyport.core.errors import NumericalConvergenceError, ValidationError
from lcmodel_pyport.core.indexing import (
    fortran_inclusive_slice,
    fortran_loop_indices,
    window_from_fortran,
)
from lcmodel_pyport.fit.regularization import (
    count_inflections_extrema,
    regula_falsi,
    second_difference_regularization,
)
from lcmodel_pyport.fit.snapshots import restore_snapshot, save_snapshot
from lcmodel_pyport.fit.solver_linear import solve_nonnegative
from lcmodel_pyport.preprocess.fft_ops import cfft_r, cfftin_r, frequency_reindex
from lcmodel_pyport.preprocess.shift_phase import (
    apply_first_order_phase,
    apply_zero_order_phase,
    integer_shift_phase_ramp,
)
from lcmodel_pyport.report.diagnostics import covariance_uncertainty

# Traceability:
# - VT-U-N-001, VT-U-N-002 map to LCModel.f:12890-12905, 12955-12963
# - VT-U-N-003 maps to LCModel.f:6079-6100
# - VT-U-N-004, VT-U-N-005 map to LCModel.f:8659-8675
# - VT-U-N-007 maps to LCModel.f:9091-9133
# - VT-U-N-008 maps to LCModel.f:8213-8233
# - VT-U-N-009 maps to LCModel.f:6164-6199
# - VT-U-N-010 maps to LCModel.f:8069-8143
# - VT-U-N-011 maps to LCModel.f:10008-10056
# - VT-U-N-012 maps to LCModel.f:10250-10314
# - VT-U-N-013 maps to LCModel.f:2396-2400
# - VT-U-I-001, VT-U-I-002 map to LCModel.f:2729-2752


def test_vt_u_n_001_fft_round_trip() -> None:
    rng = np.random.default_rng(20260309)
    for n in (16, 64):
        x = rng.normal(size=n) + 1j * rng.normal(size=n)
        recovered = cfftin_r(cfft_r(x))
        assert np.allclose(recovered, x, atol=1e-10, rtol=1e-10)


def test_vt_u_n_002_frequency_reindex_convention() -> None:
    arr = np.arange(8)
    out = frequency_reindex(arr)
    assert np.array_equal(out, np.array([4, 5, 6, 7, 0, 1, 2, 3]))


def test_vt_u_n_003_integer_shift_consistency() -> None:
    rng = np.random.default_rng(7)
    x = rng.normal(size=32) + 1j * rng.normal(size=32)
    shifted = integer_shift_phase_ramp(x, shift_points=3)
    assert np.allclose(shifted, np.roll(x, 3), atol=1e-10, rtol=1e-10)


def test_vt_u_n_004_zero_order_phase_rotation() -> None:
    x = np.ones(8, dtype=np.complex128)
    y = apply_zero_order_phase(x, 90.0)
    assert np.allclose(y.real, 0.0, atol=1e-12)
    assert np.allclose(y.imag, 1.0, atol=1e-12)


def test_vt_u_n_005_first_order_phase_ramp() -> None:
    ppm = np.array([0.0, 1.0, 2.0], dtype=float)
    x = np.ones(3, dtype=np.complex128)
    y = apply_first_order_phase(x, ppm_axis=ppm, phase_deg_per_ppm=180.0, ppm_ref=1.0)
    assert np.allclose(y.real, np.array([-1.0, 1.0, -1.0]), atol=1e-12)
    assert np.allclose(y.imag, 0.0, atol=1e-12)


def test_vt_u_n_007_nonnegative_linear_solver_validity() -> None:
    a = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    b = np.array([1.0, 2.0, 3.0])
    x = solve_nonnegative(a, b)
    assert np.all(x >= -1e-12)
    assert np.linalg.norm(a @ x - b) <= 1e-8


def test_vt_u_n_008_regula_falsi_search_behavior() -> None:
    root = regula_falsi(lambda z: z * z - 2.0, 0.0, 2.0)
    assert root == pytest.approx(np.sqrt(2.0), abs=1e-9)


def test_vt_u_n_008_regula_falsi_requires_bracket() -> None:
    with pytest.raises(ValidationError):
        regula_falsi(lambda z: z * z + 1.0, -1.0, 1.0)


def test_vt_u_n_009_regularization_matrix_construction() -> None:
    reg = second_difference_regularization(6)
    assert reg.shape == (6, 6)
    assert np.allclose(reg, reg.T, atol=1e-12)
    eigvals = np.linalg.eigvalsh(reg)
    assert np.min(eigvals) >= -1e-12


def test_vt_u_n_010_inflection_extrema_counters() -> None:
    x = np.linspace(0.0, 4.0 * np.pi, 400)
    y = np.sin(x) + 0.2
    inflections, extrema = count_inflections_extrema(y, threshold_ratio=0.05)
    assert inflections in {3, 4}
    assert extrema in {4, 5}


def test_vt_u_n_011_snapshot_save_restore_idempotence() -> None:
    state = {"a": np.array([1.0, 2.0]), "b": {"k": 3.0}}
    snap = save_snapshot(state)
    restored = restore_snapshot(snap)
    assert np.array_equal(restored["a"], state["a"])
    assert restored["b"]["k"] == state["b"]["k"]  # type: ignore[index]
    restored["a"][0] = 99.0  # type: ignore[index]
    assert state["a"][0] == 1.0


def test_vt_u_n_012_covariance_uncertainty_sanity() -> None:
    cov = np.array([[2.0, 0.3], [0.1, 1.0]])
    sym, unc = covariance_uncertainty(cov)
    assert np.allclose(sym, sym.T, atol=1e-12)
    assert np.all(unc >= 0.0)
    assert unc[0] == pytest.approx(np.sqrt(2.0))
    assert unc[1] == pytest.approx(1.0)


def test_vt_u_n_012_covariance_rejects_nonsquare() -> None:
    with pytest.raises(ValidationError):
        covariance_uncertainty(np.array([[1.0, 2.0, 3.0]]))


def test_vt_u_n_013_window_index_mapping_integrity() -> None:
    out = window_from_fortran(10, 20, 100)
    assert out == {"start_0b": 9, "end_0b_exclusive": 20, "ny": 11}


def test_vt_u_i_001_loop_bound_equivalence() -> None:
    assert fortran_loop_indices(1, 4) == [0, 1, 2, 3]
    assert fortran_loop_indices(4, 1, -1) == [3, 2, 1, 0]


def test_vt_u_i_002_slice_boundary_equivalence() -> None:
    arr = np.arange(10)
    sl = fortran_inclusive_slice(2, 5)
    assert np.array_equal(arr[sl], np.array([1, 2, 3, 4]))


def test_vt_u_n_007_solver_nonconvergence_raises() -> None:
    a = np.eye(4)
    b = np.ones(4)
    with pytest.raises(NumericalConvergenceError):
        solve_nonnegative(a, b, max_iter=0)
