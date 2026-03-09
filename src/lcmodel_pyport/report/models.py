"""Minimal report-layer data models for contract writers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConcentrationRow:
    conc: float
    pct_sd: int
    ratio_label: str
    metabolite: str


@dataclass(frozen=True)
class MiscMetrics:
    fwhm_ppm: float
    sn: int
    data_shift_ppm: float
    phase0_deg: int
    phase1_deg_per_ppm: float
    alpha_b: float
    alpha_s: float
    spline_knots: int
    ns: int
    incsid: int
    inflections: int | None = None
    extrema: int | None = None
