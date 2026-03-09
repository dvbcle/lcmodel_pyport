"""Diagnostics-related numerical helpers."""

from __future__ import annotations

import numpy as np

from lcmodel_pyport.core.errors import ValidationError


def covariance_uncertainty(covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cov = np.asarray(covariance, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValidationError("covariance must be square")
    sym = 0.5 * (cov + cov.T)
    diag = np.clip(np.diag(sym), 0.0, None)
    return sym, np.sqrt(diag)
