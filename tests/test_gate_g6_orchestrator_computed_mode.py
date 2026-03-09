from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.pipeline.orchestrator import run_case_computed_mode
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / ".tmp" / "gate_g6_orchestrator_computed"
OUT.mkdir(parents=True, exist_ok=True)


def test_orchestrator_case02_full_mode_computed() -> None:
    result = run_case_computed_mode(
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full",
        OUT,
    )
    assert result.output_generated is True
    assert result.generation_mode == "computed"
    assert result.fullfit_loaded is True
    prn = parse_print(result.output_paths["print"])
    assert prn["dofull"] is True


def test_orchestrator_case03_prelim_mode_computed() -> None:
    result = run_case_computed_mode(
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
        OUT,
    )
    assert result.output_generated is True
    assert result.generation_mode == "computed"
    assert result.fullfit_loaded is False
    table = parse_table(result.output_paths["table"])
    prn = parse_print(result.output_paths["print"])
    assert table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
    assert prn["dofull"] is False
