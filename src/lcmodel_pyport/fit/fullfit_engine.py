"""Full-fit stage checkpoint extraction (Gate G4 baseline)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lcmodel_pyport.core.errors import OutputContractError, ValidationError
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_table import parse_table


@dataclass(frozen=True)
class FullFitCheckpoint:
    dofull: bool
    phase_pair_count: int
    reference_solution_count: int
    prelim_alpha_b: float
    prelim_alpha_s: float
    final_alpha_b: float
    final_alpha_s: float
    fwhm_ppm: float
    sn: float
    data_shift_ppm: float
    phase0_deg: float
    phase1_deg_per_ppm: float
    concentration_rows: int


def run_fullfit_reference(print_path: str | Path, table_path: str | Path) -> FullFitCheckpoint:
    """Build a canonical CP-FULL-001-style checkpoint from Fortran reference outputs."""
    p = parse_print(print_path)
    t = parse_table(table_path)
    misc = t["misc_metrics"]

    if p["dofull"] is not True:
        raise ValidationError("run_fullfit_reference requires DOFULL=T output")
    if p["prelim_alpha_b"] is None or p["prelim_alpha_s"] is None:
        raise OutputContractError("Missing preliminary alpha marker in .print")
    for key in ("alpha_b", "alpha_s", "fwhm_ppm", "sn", "data_shift_ppm", "phase0_deg", "phase1_deg_per_ppm"):
        if key not in misc:
            raise OutputContractError(f"Missing misc metric {key} in .table")

    return FullFitCheckpoint(
        dofull=True,
        phase_pair_count=int(p["phase_pair_count"]),
        reference_solution_count=int(p["reference_solution_count"]),
        prelim_alpha_b=float(p["prelim_alpha_b"]),
        prelim_alpha_s=float(p["prelim_alpha_s"]),
        final_alpha_b=float(misc["alpha_b"]),
        final_alpha_s=float(misc["alpha_s"]),
        fwhm_ppm=float(misc["fwhm_ppm"]),
        sn=float(misc["sn"]),
        data_shift_ppm=float(misc["data_shift_ppm"]),
        phase0_deg=float(misc["phase0_deg"]),
        phase1_deg_per_ppm=float(misc["phase1_deg_per_ppm"]),
        concentration_rows=int(t["concentration_rows"]),
    )
