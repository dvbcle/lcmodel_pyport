"""FFT and frequency-reindex conventions matching LCModel behavior."""

from __future__ import annotations

import numpy as np

from lcmodel_pyport.core.errors import ValidationError


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
