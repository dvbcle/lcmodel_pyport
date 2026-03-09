from __future__ import annotations

import json
from pathlib import Path

import pytest

from lcmodel_pyport.core.errors import ValidationError
from lcmodel_pyport.fit.fullfit_engine import run_fullfit_reference

ROOT = Path(__file__).resolve().parents[1]
CASE02 = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
CASE03 = ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only"
CP_FULL = ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case02" / "CP-FULL-001.json"

# Traceability:
# - VT-I-005 maps to LCModel.f:352-356, 7216-7252, 7430-7433, 10008-10056
# - VT-N-001 maps to LCModel.f:10715-10720, 10732-10735, 10422-10427
# - VT-U-N-011 remains covered in tests/test_numerical_kernels_suite_e_f.py


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_vt_i_005_full_stage_checkpoint_parity_case02() -> None:
    expected = _load_json(CP_FULL)
    cp = run_fullfit_reference(
        CASE02 / "out_trace_full.print",
        CASE02 / "out_trace_full.table",
    )
    scalars = expected["scalars"]

    assert cp.dofull is scalars["dofull"]
    assert cp.phase_pair_count == scalars["phase_pair_count"]
    assert cp.reference_solution_count == scalars["reference_solution_count"]
    assert cp.prelim_alpha_b == pytest.approx(scalars["prelim_alpha_b"], abs=1e-8)
    assert cp.prelim_alpha_s == pytest.approx(scalars["prelim_alpha_s"], abs=1e-8)
    assert cp.final_alpha_b == pytest.approx(scalars["final_alpha_b"], abs=1e-8)
    assert cp.final_alpha_s == pytest.approx(scalars["final_alpha_s"], abs=1e-8)
    assert cp.concentration_rows == scalars["concentration_rows"]


def test_vt_n_001_misc_scalar_metrics_case02() -> None:
    cp = run_fullfit_reference(
        CASE02 / "out_trace_full.print",
        CASE02 / "out_trace_full.table",
    )
    assert cp.fwhm_ppm == pytest.approx(0.084, abs=1e-6)
    assert cp.sn == pytest.approx(21.0, abs=1e-9)
    assert cp.data_shift_ppm == pytest.approx(0.008, abs=1e-6)
    assert cp.phase0_deg == pytest.approx(9.0, abs=1e-9)
    assert cp.phase1_deg_per_ppm == pytest.approx(2.2, abs=1e-9)
    assert cp.final_alpha_b > 0.0
    assert cp.final_alpha_s > 0.0


def test_fullfit_reference_rejects_prelim_only_case() -> None:
    with pytest.raises(ValidationError):
        run_fullfit_reference(
            CASE03 / "out_trace_prelim.print",
            CASE03 / "out_trace_prelim.table",
        )
