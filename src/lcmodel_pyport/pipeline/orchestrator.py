"""Reference-mode orchestration across staged components."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.fit.fullfit_engine import FullFitCheckpoint, run_fullfit_computed, run_fullfit_reference
from lcmodel_pyport.fit.prelim_engine import PrelimCheckpoint, run_prelim_computed
from lcmodel_pyport.io.basis_reader import BasisDataset, read_basis_dataset
from lcmodel_pyport.io.raw_reader import RawDataset, read_raw_dataset
from lcmodel_pyport.pipeline.output_stage import (
    generate_outputs_from_computed_case,
    generate_outputs_from_reference_case,
)
from lcmodel_pyport.verify.parsers_print import parse_print


@dataclass(frozen=True)
class OrchestrationResult:
    case_dir: Path
    dofull: bool
    control_loaded: bool
    raw_loaded: bool
    basis_loaded: bool
    prelim_loaded: bool
    fullfit_loaded: bool
    output_generated: bool
    generation_mode: str
    output_paths: dict[str, Path]


def _find_control_file(case_dir: Path) -> Path:
    for name in ("control_trace_full.file", "control_trace_prelim.file", "control.file"):
        path = case_dir / name
        if path.exists():
            return path
    raise FileNotFoundError(f"No control file found in {case_dir}")


def _find_reference_file(case_dir: Path, suffix: str) -> Path:
    candidates = sorted(case_dir.glob(f"*{suffix}"))
    if not candidates:
        raise FileNotFoundError(f"No {suffix} file found in {case_dir}")
    return candidates[0]


def run_case_reference_mode(case_dir: str | Path, output_root: str | Path) -> OrchestrationResult:
    """Run stage-orchestrated reference-mode flow for a single fixture case."""
    case_path = Path(case_dir)
    output_root_path = Path(output_root)
    output_root_path.mkdir(parents=True, exist_ok=True)

    control_path = _find_control_file(case_path)
    cfg = build_control_config(control_path.read_text(encoding="utf-8"))

    raw: RawDataset = read_raw_dataset(case_path / cfg.filraw, expected_nunfil=cfg.nunfil)
    basis: BasisDataset = read_basis_dataset(case_path / cfg.filbas)
    prelim = parse_print(_find_reference_file(case_path, ".print"))

    _ = raw, basis, prelim  # explicit stage materialization in reference mode
    fullfit: FullFitCheckpoint | None = None
    if cfg.dofull:
        fullfit = run_fullfit_reference(
            _find_reference_file(case_path, ".print"),
            _find_reference_file(case_path, ".table"),
        )
    _ = fullfit

    out_dir = output_root_path / case_path.name
    output_paths = generate_outputs_from_reference_case(case_path, out_dir)

    return OrchestrationResult(
        case_dir=case_path,
        dofull=cfg.dofull,
        control_loaded=True,
        raw_loaded=True,
        basis_loaded=True,
        prelim_loaded=True,
        fullfit_loaded=cfg.dofull,
        output_generated=all(path.exists() for path in output_paths.values()),
        generation_mode="reference",
        output_paths=output_paths,
    )


def run_case_computed_mode(case_dir: str | Path, output_root: str | Path) -> OrchestrationResult:
    """Run stage flow with computed output generation (no reference output parsing for writes)."""
    case_path = Path(case_dir)
    output_root_path = Path(output_root)
    output_root_path.mkdir(parents=True, exist_ok=True)

    control_path = _find_control_file(case_path)
    cfg = build_control_config(control_path.read_text(encoding="utf-8"))
    raw: RawDataset = read_raw_dataset(case_path / cfg.filraw, expected_nunfil=cfg.nunfil)
    basis: BasisDataset = read_basis_dataset(case_path / cfg.filbas)
    prelim: PrelimCheckpoint = run_prelim_computed(cfg, raw, basis)
    fullfit: FullFitCheckpoint | None = None
    if cfg.dofull:
        fullfit = run_fullfit_computed(cfg, raw, basis, prelim)

    out_dir = output_root_path / case_path.name
    output_paths = generate_outputs_from_computed_case(case_path, out_dir)
    return OrchestrationResult(
        case_dir=case_path,
        dofull=cfg.dofull,
        control_loaded=True,
        raw_loaded=True,
        basis_loaded=True,
        prelim_loaded=prelim is not None,
        fullfit_loaded=fullfit is not None,
        output_generated=all(path.exists() for path in output_paths.values()),
        generation_mode="computed",
        output_paths=output_paths,
    )
