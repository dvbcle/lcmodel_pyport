"""Helpers for explicit Fortran 1-based indexing conversions."""

from __future__ import annotations

from lcmodel_pyport.core.errors import ValidationError


def fortran_loop_indices(start_1b: int, end_1b: int, step: int = 1) -> list[int]:
    """Return 0-based indices visited by an inclusive Fortran DO loop."""
    if step == 0:
        raise ValidationError("step cannot be zero")
    if step > 0:
        values = range(start_1b, end_1b + 1, step)
    else:
        values = range(start_1b, end_1b - 1, step)
    return [i - 1 for i in values]


def fortran_inclusive_slice(start_1b: int, end_1b: int) -> slice:
    """Convert inclusive 1-based [start,end] to Python slice [start-1:end]."""
    if start_1b < 1 or end_1b < start_1b:
        raise ValidationError("invalid Fortran inclusive bounds")
    return slice(start_1b - 1, end_1b)


def window_from_fortran(ldatst: int, ldaten: int, ndata: int) -> dict[str, int]:
    """Translate LCModel window bounds to Python offsets and length."""
    if ldatst < 1 or ldaten < ldatst or ldaten > ndata:
        raise ValidationError("invalid LDATST/LDATEN bounds")
    start_0b = ldatst - 1
    end_0b_exclusive = ldaten
    ny = ldaten - ldatst + 1
    return {"start_0b": start_0b, "end_0b_exclusive": end_0b_exclusive, "ny": ny}
