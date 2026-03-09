from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
CASE02 = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
CASE03 = ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only"

# Traceability:
# - VT-C-002 maps to LCModel.f:10423-10427 and 10804-10808
# - VT-C-003 maps to LCModel.f:10775-10787
# - VT-C-005 maps to LCModel.f:352-356, 5935-5941, 7250-7252, 7430-7433


def test_vt_c_002_table_section_contract() -> None:
    parsed = parse_table(CASE02 / "out_trace_full.table")
    assert parsed["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]


def test_vt_c_003_coord_section_contract() -> None:
    parsed = parse_coord(CASE02 / "out_trace_full.coord")
    pos = parsed["positions"]
    assert "ppm_axis" in pos
    assert "phased_data" in pos
    assert "fit" in pos
    assert "background" in pos
    assert pos["ppm_axis"] < pos["phased_data"] < pos["fit"] < pos["background"]


def test_vt_c_005_branch_marker_contract_dofull() -> None:
    full = parse_print(CASE02 / "out_trace_full.print")
    prelim = parse_print(CASE03 / "out_trace_prelim.print")

    assert full["dofull"] is True
    assert prelim["dofull"] is False
    assert len(full["markers"]) >= 2
    assert prelim["markers"] == []

