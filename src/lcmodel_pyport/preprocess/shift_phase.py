"""Shift and phase operators used by preliminary/full fitting stages."""

from __future__ import annotations

import numpy as np

from lcmodel_pyport.core.errors import ValidationError


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
