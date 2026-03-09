from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.pipeline.output_stage import generate_outputs_from_reference_case
from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_corraw import parse_corraw
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / ".tmp" / "gate_g5_output_stage"
OUT.mkdir(parents=True, exist_ok=True)

# Traceability:
# - VT-C-002/003/004/005 map to LCModel.f:10423-10427, 10775-10787, 10810-10833, 352-356/7430-7433


def test_output_stage_generation_from_reference_case02() -> None:
    paths = generate_outputs_from_reference_case(
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full",
        OUT / "case02",
    )
    assert all(path.exists() for path in paths.values())

    table = parse_table(paths["table"])
    coord = parse_coord(paths["coord"])
    cor = parse_corraw(paths["corraw"])
    prn = parse_print(paths["print"])
    assert table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
    assert "background" in coord["positions"]
    assert cor["n_points"] == 1024
    assert prn["dofull"] is True


def test_output_stage_generation_from_reference_case03() -> None:
    paths = generate_outputs_from_reference_case(
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
        OUT / "case03",
    )
    prn = parse_print(paths["print"])
    table = parse_table(paths["table"])
    assert prn["dofull"] is False
    assert table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
