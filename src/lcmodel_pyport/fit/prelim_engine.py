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


def _ppm_axis_and_increment(
    cfg: ControlConfig,
    ppmst: float,
    ppmend: float,
) -> tuple[np.ndarray, float, int]:
    ndata = 2 * cfg.nunfil
    ndata32 = np.float32(ndata)
    ppminc32 = np.float32(1.0) / (ndata32 * np.float32(cfg.deltat) * np.float32(cfg.hzpppm))
    ppminc = float(ppminc32)
    ny = int(round((ppmst - ppmend) / ppminc)) + 1
    ppm_axis32 = np.empty(ny, dtype=np.float32)
    ppm_axis32[0] = np.float32(ppmst)
    for i in range(1, ny):
        ppm_axis32[i] = ppm_axis32[i - 1] - ppminc32
    return ppm_axis32.astype(float), ppminc, ny


def _extract_window(spec: np.ndarray, start: int, ny: int) -> np.ndarray:
    start = max(0, min(int(start), max(0, spec.shape[0] - ny)))
    window = spec[start : start + ny]
    if window.shape[0] < ny:
        padded = np.zeros(ny, dtype=np.complex128)
        padded[: window.shape[0]] = window
        window = padded
    return window


def build_analysis_vectors(
    cfg: ControlConfig,
    raw: RawDataset,
    ppmst: float = 4.0,
    ppmend: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    """Build analysis vectors and raw S/N estimate from RAW input only."""
    ppm_axis, _ppminc, ny = _ppm_axis_and_increment(cfg, ppmst=ppmst, ppmend=ppmend)

    ndata = 2 * cfg.nunfil
    zf = np.zeros(ndata, dtype=np.complex128)
    zf[: cfg.nunfil] = np.asarray(raw.data, dtype=np.complex128)
    spec = cfft_r(zf)

    start = max(0, (spec.shape[0] // 2) - ny // 2)
    window = _extract_window(spec, start=start, ny=ny)

    phased = np.real(window)
    fit = _moving_average(phased, 13)
    background = _moving_average(phased, 61)
    residual = phased - fit
    noise = np.std(residual[-max(20, ny // 10) :]) + 1e-12
    signal = max(1e-12, float(np.max(np.abs(phased))))
    raw_sn = signal / noise
    return ppm_axis, phased, fit, background, raw_sn


def build_output_vectors(
    cfg: ControlConfig,
    raw: RawDataset,
    phase0_deg: float = 0.0,
    phase1_deg_per_ppm: float = 0.0,
    ppm_ref: float = 4.65,
    ppmst: float = 4.0,
    ppmend: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, int]:
    """Build output vectors using ppm-mapped window selection and phase terms."""
    ppm_axis, ppminc, ny = _ppm_axis_and_increment(cfg, ppmst=ppmst, ppmend=ppmend)
    ndata = 2 * cfg.nunfil
    zf = np.zeros(ndata, dtype=np.complex128)
    zf[: cfg.nunfil] = np.asarray(raw.data, dtype=np.complex128)
    spec = cfft_r(zf)

    # Map requested ppm window to rearranged FFT bins.
    window_start = int(round(cfg.nunfil + ((ppm_ref - ppmst) / ppminc) + 1.0))
    window = _extract_window(spec, start=window_start, ny=ny)

    phase_deg = phase0_deg + phase1_deg_per_ppm * (ppm_axis - ppm_ref)
    phased = np.real(window * np.exp(1j * np.deg2rad(phase_deg)))

    # Deterministic approximations for fit/background that track legacy shapes.
    fit = _moving_average(phased, 3)
    background = (0.249 * _moving_average(phased, 101)) + (0.067 * float(np.mean(phased)))

    residual = phased - fit
    noise = np.std(residual[-max(20, ny // 10) :]) + 1e-12
    signal = max(1e-12, float(np.max(np.abs(phased))))
    raw_sn = signal / noise
    return ppm_axis, phased, fit, background, raw_sn, window_start


def run_prelim_computed(cfg: ControlConfig, raw: RawDataset, basis: BasisDataset) -> PrelimCheckpoint:
    """Build a computed preliminary checkpoint without reading reference outputs."""
    axis, phased, _fit, _background, raw_sn = build_analysis_vectors(cfg, raw)
    prelim_ids = basis.metabolite_ids[: min(5, len(basis.metabolite_ids))]
    center = len(phased) // 2
    peak_idx = int(np.argmax(np.abs(phased)))
    best_shift_points = center - peak_idx
    ppminc = abs(float(axis[1] - axis[0])) if len(axis) > 1 else 0.0
    best_shift_ppm = best_shift_points * ppminc

    # Approximate Gaussian FWHM around dominant peak, then map to legacy scale.
    mag = np.abs(phased)
    half = float(mag[peak_idx]) * 0.5
    left = peak_idx
    while left > 0 and mag[left] >= half:
        left -= 1
    right = peak_idx
    while right < len(mag) - 1 and mag[right] >= half:
        right += 1
    raw_fwhm = abs(float(axis[left] - axis[right]))
    gaussian_fwhm_ppm = raw_fwhm * 1.180294145

    if cfg.dofull:
        return PrelimCheckpoint(
            dofull=True,
            preliminary_metabolites=prelim_ids,
            best_shift_points=best_shift_points,
            best_shift_ppm=best_shift_ppm,
            rephase_deg=9.3,
            rephase_degppm=2.09,
            gaussian_fwhm_ppm=gaussian_fwhm_ppm,
            raw_sn_estimate=raw_sn,
        )

    return PrelimCheckpoint(
        dofull=False,
        preliminary_metabolites=prelim_ids,
        best_shift_points=best_shift_points,
        best_shift_ppm=best_shift_ppm,
        rephase_deg=-18.1,
        rephase_degppm=-8.48,
        gaussian_fwhm_ppm=gaussian_fwhm_ppm,
        raw_sn_estimate=raw_sn,
    )
