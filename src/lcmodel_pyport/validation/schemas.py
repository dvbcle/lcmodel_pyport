"""Explicit schema/type checks for gate G1."""

from __future__ import annotations

from lcmodel_pyport.config.models import ControlConfig, RawDataset
from lcmodel_pyport.core.errors import ValidationError


def _require_type(name: str, value: object, expected: type) -> None:
    if not isinstance(value, expected):
        raise ValidationError(f"{name} must be {expected.__name__}, got {type(value).__name__}")


def validate_control_config(cfg: ControlConfig) -> None:
    _require_type("nunfil", cfg.nunfil, int)
    _require_type("deltat", cfg.deltat, float)
    _require_type("hzpppm", cfg.hzpppm, float)
    _require_type("filbas", cfg.filbas, str)
    _require_type("filraw", cfg.filraw, str)
    _require_type("filps", cfg.filps, str)
    _require_type("dofull", cfg.dofull, bool)
    _require_type("lprint", cfg.lprint, int)
    _require_type("lcoord", cfg.lcoord, int)
    _require_type("ltable", cfg.ltable, int)
    _require_type("lcoraw", cfg.lcoraw, int)
    _require_type("lps", cfg.lps, int)
    if cfg.nunfil <= 0:
        raise ValidationError("nunfil must be > 0")
    if cfg.deltat <= 0:
        raise ValidationError("deltat must be > 0")
    if cfg.hzpppm <= 0:
        raise ValidationError("hzpppm must be > 0")


def validate_raw_dataset(dataset: RawDataset, expected_nunfil: int | None = None) -> None:
    if expected_nunfil is not None and len(dataset.data) != expected_nunfil:
        raise ValidationError(
            f"raw point count mismatch: expected {expected_nunfil}, got {len(dataset.data)}"
        )
    if dataset.nmid.fmtdat.strip() == "":
        raise ValidationError("NMID.FMTDAT must not be blank")

