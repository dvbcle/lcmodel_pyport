"""Tolerance profile helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToleranceProfile:
    float_abs: float = 1e-8
    float_rel: float = 1e-4
    vector_rmse: float = 1e-5
    vector_max_abs: float = 1e-4

