from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.pipeline.orchestrator import run_case_reference_mode
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / ".tmp" / "gate_g6_orchestrator"
OUT.mkdir(parents=True, exist_ok=True)

# Traceability:
# - VT-I-001..VT-I-007 (partial reference-mode orchestration path)
# - VT-C-001 output presence
# - VT-C-005 DOFULL branch behavior


def test_orchestrator_case02_full_mode_generates_outputs() -> None:
    result = run_case_reference_mode(
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full",
        OUT,
    )
    assert result.control_loaded is True
    assert result.raw_loaded is True
    assert result.basis_loaded is True
    assert result.prelim_loaded is True
    assert result.fullfit_loaded is True
    assert result.output_generated is True
    assert all(path.exists() for path in result.output_paths.values())

    prn = parse_print(result.output_paths["print"])
    assert prn["dofull"] is True
    assert prn["phase_pair_count"] >= 1


def test_orchestrator_case03_prelim_mode_skips_fullfit() -> None:
    result = run_case_reference_mode(
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
        OUT,
    )
    assert result.dofull is False
    assert result.fullfit_loaded is False
    assert result.output_generated is True

    prn = parse_print(result.output_paths["print"])
    table = parse_table(result.output_paths["table"])
    assert prn["dofull"] is False
    assert table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
