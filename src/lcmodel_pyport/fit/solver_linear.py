"""Linear constrained solvers."""

from __future__ import annotations

import numpy as np

from lcmodel_pyport.core.errors import NumericalConvergenceError, ValidationError


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
