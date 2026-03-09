from __future__ import annotations

import json
from pathlib import Path

import pytest

from lcmodel_pyport.io.basis_reader import read_basis_dataset
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_ps import parse_ps
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
CASE02 = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
CASE03 = ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only"
CP_BASIS = ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case02" / "CP-BASIS-001.json"
CP_PRELIM = ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case03" / "CP-PRELIM-001.json"

# Traceability:
# - VT-I-003 maps to LCModel.f:3216-3238 and 3297-3306
# - VT-I-004 maps to LCModel.f:331-346, 5441-5444, 6962-7025
# - VT-S-001 maps to LCModel.f:5935-5941 and 11476-11483
# - VT-S-002 maps to LCModel.f:352-356 and 10422-10427
# - VT-C-005 already covered in test_contract_parsers.py (branch marker contract)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_vt_i_003_basis_stage_checkpoint_parity_case02() -> None:
    expected = _load_json(CP_BASIS)
    basis = read_basis_dataset(CASE02 / "3t.basis")
    printed = parse_print(CASE02 / "out_trace_full.print")

    assert basis.idbasi == expected["scalars"]["basis_set_id"]
    assert basis.fmtdat == expected["scalars"]["fmtbas"]
    assert basis.badelt == pytest.approx(expected["scalars"]["badelt"])
    assert basis.ndatab == expected["scalars"]["ndatab"]
    assert len(basis.metabolite_ids) == expected["scalars"]["basis_file_entry_count"]
    assert printed["preliminary_metabolites"] == expected["vectors"]["preliminary_metabolites"]
    assert len(printed["preliminary_metabolites"]) == expected["scalars"]["preliminary_selected_count"]
    assert len(printed["final_metabolites"]) == expected["scalars"]["final_selected_count"]


def test_vt_i_004_preliminary_stage_checkpoint_parity_case03() -> None:
    expected = _load_json(CP_PRELIM)
    parsed = parse_print(CASE03 / "out_trace_prelim.print")

    assert parsed["starting_shift_count"] == expected["scalars"]["starting_shift_count"]
    assert parsed["best_shift_points"] == expected["scalars"]["best_shift_points"]
    assert parsed["best_shift_ppm"] == pytest.approx(expected["scalars"]["best_shift_ppm"], abs=1e-6)
    assert parsed["rephase_deg"] == pytest.approx(expected["scalars"]["rephase_deg"], abs=1e-3)
    assert parsed["rephase_degppm"] == pytest.approx(expected["scalars"]["rephase_degppm"], abs=1e-3)
    assert parsed["gaussian_fwhm_ppm"] == pytest.approx(
        expected["scalars"]["gaussian_fwhm_ppm"], abs=1e-4
    )
    assert parsed["has_optimal_shift_section"] is expected["flags"]["has_optimal_shift_section"]


def test_vt_s_001_mode_specific_behavior_crude_model_marker() -> None:
    prelim_ps = parse_ps(CASE03 / "out_trace_prelim.ps")
    full_ps = parse_ps(CASE02 / "out_trace_full.ps")
    assert prelim_ps["has_crude_model_marker"] is True
    assert full_ps["has_crude_model_marker"] is False


def test_vt_s_002_concentration_regime_check_full_vs_prelim() -> None:
    full = parse_table(CASE02 / "out_trace_full.table")
    prelim = parse_table(CASE03 / "out_trace_prelim.table")
    assert full["concentration_rows"] > prelim["concentration_rows"]
    assert full["concentration_rows"] == 35
    assert prelim["concentration_rows"] == 5
