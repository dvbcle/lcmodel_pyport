"""Regularization/search kernels for fitting."""

from __future__ import annotations

from typing import Callable

import numpy as np

from lcmodel_pyport.core.errors import NumericalConvergenceError, ValidationError


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
