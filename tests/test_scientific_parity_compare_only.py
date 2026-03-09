from __future__ import annotations

from pathlib import Path
from typing import Any

from lcmodel_pyport.verify.evidence import run_external_dataset_evidence

ROOT = Path(__file__).resolve().parents[1]

# Traceability:
# - VT-N-005 / VT-N-006 compare-only scientific parity gates
# - Fortran references: LCModel.f:10423-10427, 10775-10787, 10810-10833


def _stage(evidence: dict[str, Any], stage_name: str) -> dict[str, Any]:
    for stage in evidence["stages"]:
        if stage["stage"] == stage_name:
            return stage
    raise AssertionError(f"Stage not found in evidence: {stage_name}")


def _numeric_case(evidence: dict[str, Any], case_id: str) -> dict[str, Any]:
    numeric = _stage(evidence, "output_numeric_regression_stage")
    return numeric["checks"]["cases"][case_id]


def test_compare_only_generation_paths_do_not_write_reference_artifacts() -> None:
    evidence = run_external_dataset_evidence(ROOT)
    generation = _stage(evidence, "python_pipeline_e2e_generation")
    generated_files = generation["checks"]["generated_files"]
    generated_root = str(ROOT / "tests" / ".tmp" / "generated_external_cases")

    for case_id in ("case02", "case03"):
        for path in generated_files[case_id].values():
            assert generated_root in path
            assert "artifacts\\step4_exec" not in path


def test_vt_n_005_external_dataset_scientific_parity_gate() -> None:
    evidence = run_external_dataset_evidence(ROOT)
    numeric = _stage(evidence, "output_numeric_regression_stage")

    assert numeric["status"] == "pass"
    assert _numeric_case(evidence, "case02")["overall_case_ok"] is True
    assert _numeric_case(evidence, "case03")["overall_case_ok"] is True


def test_vt_n_006_compare_only_scalar_and_concentration_gates() -> None:
    evidence = run_external_dataset_evidence(ROOT)

    for case_id in ("case02", "case03"):
        case_checks = _numeric_case(evidence, case_id)
        assert case_checks["misc_scalars_within_tolerance"] is True
        assert case_checks["concentration_rows_match"] is True

