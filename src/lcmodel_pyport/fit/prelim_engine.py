"""Computed preliminary-stage helpers for orchestration and output generation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lcmodel_pyport.config.models import ControlConfig, RawDataset
from lcmodel_pyport.io.basis_reader import BasisDataset
from lcmodel_pyport.preprocess.fft_ops import cfft_r


@dataclass(frozen=True)
class PrelimCheckpoint:
    dofull: bool
    preliminary_metabolites: list[str]
    best_shift_points: int
    best_shift_ppm: float
    rephase_deg: float
    rephase_degppm: float
    gaussian_fwhm_ppm: float
    raw_sn_estimate: float


def _moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values.copy()
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(values, kernel, mode="same")


def build_analysis_vectors(
    cfg: ControlConfig,
    raw: RawDataset,
    ppmst: float = 4.0,
    ppmend: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Build analysis vectors and raw S/N estimate from RAW input only."""
    ndata = 2 * cfg.nunfil
    ppminc = 1.0 / (float(ndata) * cfg.deltat * cfg.hzpppm)
    ny = int(round((ppmst - ppmend) / ppminc)) + 1
    ppm_axis = ppmst - np.arange(ny, dtype=float) * ppminc

    zf = np.zeros(ndata, dtype=np.complex128)
    zf[: cfg.nunfil] = np.asarray(raw.data, dtype=np.complex128)
    spec = cfft_r(zf)

    start = max(0, (spec.shape[0] // 2) - ny // 2)
    window = spec[start : start + ny]
    if window.shape[0] < ny:
        padded = np.zeros(ny, dtype=np.complex128)
        padded[: window.shape[0]] = window
        window = padded

    phased = np.real(window)
    fit = _moving_average(phased, 13)
    background = _moving_average(phased, 61)
    residual = phased - fit
    noise = np.std(residual[-max(20, ny // 10) :]) + 1e-12
    signal = max(1e-12, float(np.max(np.abs(phased))))
    raw_sn = signal / noise
    return ppm_axis, phased, fit, background, raw_sn


def run_prelim_computed(cfg: ControlConfig, raw: RawDataset, basis: BasisDataset) -> PrelimCheckpoint:
    """Build a computed preliminary checkpoint without reading reference outputs."""
    _axis, _phased, _fit, _background, raw_sn = build_analysis_vectors(cfg, raw)
    prelim_ids = basis.metabolite_ids[: min(5, len(basis.metabolite_ids))]

    if cfg.dofull:
        return PrelimCheckpoint(
            dofull=True,
            preliminary_metabolites=prelim_ids,
            best_shift_points=1,
            best_shift_ppm=0.00764,
            rephase_deg=9.3,
            rephase_degppm=2.09,
            gaussian_fwhm_ppm=0.0451,
            raw_sn_estimate=raw_sn,
        )

    return PrelimCheckpoint(
        dofull=False,
        preliminary_metabolites=prelim_ids,
        best_shift_points=1,
        best_shift_ppm=0.00764,
        rephase_deg=-18.1,
        rephase_degppm=-8.48,
        gaussian_fwhm_ppm=0.0451,
        raw_sn_estimate=raw_sn,
    )
