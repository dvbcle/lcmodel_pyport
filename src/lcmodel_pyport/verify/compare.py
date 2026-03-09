"""Simple comparator helpers for parity checks."""

from __future__ import annotations

from math import sqrt
from typing import Iterable


def rmse(a: Iterable[float], b: Iterable[float]) -> float:
    av = list(a)
    bv = list(b)
    if len(av) != len(bv):
        raise ValueError("vector lengths differ")
    if not av:
        return 0.0
    return sqrt(sum((x - y) ** 2 for x, y in zip(av, bv)) / len(av))


def max_abs_delta(a: Iterable[float], b: Iterable[float]) -> float:
    av = list(a)
    bv = list(b)
    if len(av) != len(bv):
        raise ValueError("vector lengths differ")
    if not av:
        return 0.0
    return max(abs(x - y) for x, y in zip(av, bv))


def close_scalar(actual: float, expected: float, abs_tol: float, rel_tol: float) -> bool:
    delta = abs(actual - expected)
    scale = max(abs(expected), 1.0)
    return delta <= max(abs_tol, rel_tol * scale)
