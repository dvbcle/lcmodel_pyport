from __future__ import annotations

import json
from pathlib import Path

import pytest

from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.fit.fullfit_engine import run_fullfit_computed
from lcmodel_pyport.fit.prelim_engine import run_prelim_computed
from lcmodel_pyport.io.basis_reader import read_basis_dataset
from lcmodel_pyport.io.raw_reader import read_raw_dataset

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_prelim_computed_checkpoint_case03_matches_cp_prelim_001() -> None:
    case = ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only"
    cfg = build_control_config((case / "control_trace_prelim.file").read_text(encoding="utf-8"))
    raw = read_raw_dataset(case / "data.raw", expected_nunfil=cfg.nunfil)
    basis = read_basis_dataset(case / "3t.basis")

    cp = run_prelim_computed(cfg, raw, basis)
    expected = _load_json(ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case03" / "CP-PRELIM-001.json")
    scalars = expected["scalars"]

    assert cp.dofull is False
    assert cp.best_shift_points == scalars["best_shift_points"]
    assert cp.best_shift_ppm == pytest.approx(scalars["best_shift_ppm"], abs=1e-5)
    assert cp.rephase_deg == pytest.approx(scalars["rephase_deg"], abs=0.2)
    assert cp.rephase_degppm == pytest.approx(scalars["rephase_degppm"], abs=0.2)
    assert cp.gaussian_fwhm_ppm == pytest.approx(scalars["gaussian_fwhm_ppm"], abs=1e-5)


def test_fullfit_computed_checkpoint_case02_matches_cp_full_001() -> None:
    case = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
    cfg = build_control_config((case / "control_trace_full.file").read_text(encoding="utf-8"))
    raw = read_raw_dataset(case / "data.raw", expected_nunfil=cfg.nunfil)
    basis = read_basis_dataset(case / "3t.basis")
    prelim = run_prelim_computed(cfg, raw, basis)

    cp = run_fullfit_computed(cfg, raw, basis, prelim)
    expected = _load_json(ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case02" / "CP-FULL-001.json")
    scalars = expected["scalars"]

    assert cp.dofull is scalars["dofull"]
    assert cp.phase_pair_count == scalars["phase_pair_count"]
    assert cp.reference_solution_count == scalars["reference_solution_count"]
    assert cp.prelim_alpha_b == pytest.approx(scalars["prelim_alpha_b"], abs=1e-9)
    assert cp.prelim_alpha_s == pytest.approx(scalars["prelim_alpha_s"], abs=1e-9)
    assert cp.final_alpha_b == pytest.approx(scalars["final_alpha_b"], abs=1e-9)
    assert cp.final_alpha_s == pytest.approx(scalars["final_alpha_s"], abs=1e-9)
    assert cp.fwhm_ppm == pytest.approx(scalars["fwhm_ppm"], abs=1e-9)
    assert cp.sn == pytest.approx(scalars["sn"], abs=1e-9)
    assert cp.data_shift_ppm == pytest.approx(scalars["data_shift_ppm"], abs=1e-9)
    assert cp.phase0_deg == pytest.approx(scalars["phase0_deg"], abs=1e-9)
    assert cp.phase1_deg_per_ppm == pytest.approx(scalars["phase1_deg_per_ppm"], abs=1e-9)
    assert cp.concentration_rows == scalars["concentration_rows"]
