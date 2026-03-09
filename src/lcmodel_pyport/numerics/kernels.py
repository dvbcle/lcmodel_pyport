"""Numerical kernels extracted for unit-level verification."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable

import numpy as np

from lcmodel_pyport.core.errors import NumericalConvergenceError, ValidationError


def frequency_reindex(values: np.ndarray) -> np.ndarray:
    """Rearrange spectrum by swapping first/second half (Fortran CFFT_r convention)."""
    arr = np.asarray(values)
    n = arr.shape[0]
    if n % 2 != 0:
        raise ValidationError("frequency_reindex requires even-length arrays")
    half = n // 2
    return np.concatenate((arr[half:], arr[:half]))


def cfft_r(data: np.ndarray) -> np.ndarray:
    """FFT with LCModel-style normalization and frequency rearrangement."""
    arr = np.asarray(data, dtype=np.complex128)
    n = arr.shape[0]
    return frequency_reindex(np.fft.fft(arr) / np.sqrt(float(n)))


def cfftin_r(rearranged_ft: np.ndarray) -> np.ndarray:
    """Inverse transform for rearranged FT (inverse of ``cfft_r``)."""
    arr = np.asarray(rearranged_ft, dtype=np.complex128)
    n = arr.shape[0]
    ft = frequency_reindex(arr)
    return np.fft.ifft(ft) * np.sqrt(float(n))


def integer_shift_phase_ramp(data: np.ndarray, shift_points: int) -> np.ndarray:
    """Apply an integer cyclic shift via Fourier-domain phase ramp."""
    arr = np.asarray(data, dtype=np.complex128)
    n = arr.shape[0]
    k = np.arange(n, dtype=float)
    ramp = np.exp(-2j * np.pi * k * float(shift_points) / float(n))
    return np.fft.ifft(np.fft.fft(arr) * ramp)


def apply_zero_order_phase(data: np.ndarray, phase_deg: float) -> np.ndarray:
    arr = np.asarray(data, dtype=np.complex128)
    return arr * np.exp(1j * np.deg2rad(phase_deg))


def apply_first_order_phase(
    data: np.ndarray,
    ppm_axis: np.ndarray,
    phase_deg_per_ppm: float,
    ppm_ref: float,
    zero_phase_deg: float = 0.0,
) -> np.ndarray:
    arr = np.asarray(data, dtype=np.complex128)
    ppm = np.asarray(ppm_axis, dtype=float)
    if arr.shape[0] != ppm.shape[0]:
        raise ValidationError("data and ppm_axis length mismatch")
    phase_deg = zero_phase_deg + phase_deg_per_ppm * (ppm - ppm_ref)
    return arr * np.exp(1j * np.deg2rad(phase_deg))


def solve_nonnegative(
    a: np.ndarray,
    b: np.ndarray,
    tol: float = 1e-10,
    max_iter: int = 5000,
) -> np.ndarray:
    """Projected-gradient nonnegative least-squares approximation."""
    mat = np.asarray(a, dtype=float)
    vec = np.asarray(b, dtype=float)
    if mat.ndim != 2:
        raise ValidationError("a must be 2D")
    if vec.ndim != 1 or vec.shape[0] != mat.shape[0]:
        raise ValidationError("b must be 1D with length equal to a.shape[0]")

    x = np.zeros(mat.shape[1], dtype=float)
    lipschitz = float(np.linalg.norm(mat, ord=2) ** 2)
    step = 1.0 / (lipschitz + 1e-12)

    for _ in range(max_iter):
        grad = mat.T @ (mat @ x - vec)
        next_x = np.maximum(0.0, x - step * grad)
        if np.linalg.norm(next_x - x) <= tol * max(1.0, np.linalg.norm(next_x)):
            return next_x
        x = next_x
    raise NumericalConvergenceError("solve_nonnegative failed to converge")


def regula_falsi(
    fn: Callable[[float], float],
    lo: float,
    hi: float,
    tol: float = 1e-10,
    max_iter: int = 200,
) -> float:
    """Bracketing root-find with regula-falsi update."""
    flo = fn(lo)
    fhi = fn(hi)
    if flo == 0.0:
        return lo
    if fhi == 0.0:
        return hi
    if flo * fhi > 0:
        raise ValidationError("regula_falsi requires bracket with opposite signs")

    x = lo
    for _ in range(max_iter):
        x = (lo * fhi - hi * flo) / (fhi - flo)
        fx = fn(x)
        if abs(fx) <= tol:
            return x
        if flo * fx < 0:
            hi, fhi = x, fx
        else:
            lo, flo = x, fx
    raise NumericalConvergenceError("regula_falsi did not converge within max_iter")


def second_difference_regularization(n: int) -> np.ndarray:
    if n < 3:
        raise ValidationError("n must be >= 3")
    d = np.zeros((n - 2, n), dtype=float)
    for i in range(n - 2):
        d[i, i] = 1.0
        d[i, i + 1] = -2.0
        d[i, i + 2] = 1.0
    return d.T @ d


def count_inflections_extrema(values: np.ndarray, threshold_ratio: float = 0.0) -> tuple[int, int]:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size < 5:
        raise ValidationError("values must be 1D with at least 5 points")
    threshold = float(np.max(np.abs(arr)) * max(0.0, threshold_ratio))

    d1 = np.diff(arr)
    d2 = np.diff(d1)

    extrema = 0
    for i in range(1, d1.size):
        if d1[i - 1] == 0 or d1[i] == 0:
            continue
        if d1[i - 1] * d1[i] < 0 and abs(arr[i]) >= threshold:
            extrema += 1

    inflections = 0
    for i in range(1, d2.size):
        if d2[i - 1] == 0 or d2[i] == 0:
            continue
        if d2[i - 1] * d2[i] < 0 and abs(arr[i + 1]) >= threshold:
            inflections += 1
    return inflections, extrema


@dataclass(frozen=True)
class Snapshot:
    state: dict[str, object]


def save_snapshot(state: dict[str, object]) -> Snapshot:
    return Snapshot(state=deepcopy(state))


def restore_snapshot(snapshot: Snapshot) -> dict[str, object]:
    return deepcopy(snapshot.state)


def covariance_uncertainty(covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cov = np.asarray(covariance, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValidationError("covariance must be square")
    sym = 0.5 * (cov + cov.T)
    diag = np.clip(np.diag(sym), 0.0, None)
    return sym, np.sqrt(diag)
