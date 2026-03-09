from __future__ import annotations

import shutil
from pathlib import Path

from lcmodel_pyport.pipeline.output_stage import generate_outputs_from_computed_case
from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_corraw import parse_corraw
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_ps import parse_ps
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / ".tmp" / "gate_g5_output_stage_computed"
OUT.mkdir(parents=True, exist_ok=True)


def _copy_case_inputs_only(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.file", "*.raw", "*.basis"):
        for file in source.glob(pattern):
            shutil.copy2(file, target / file.name)


def test_output_stage_generation_from_computed_case02() -> None:
    paths = generate_outputs_from_computed_case(
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full",
        OUT / "case02",
    )
    assert all(path.exists() for path in paths.values())
    table = parse_table(paths["table"])
    coord = parse_coord(paths["coord"])
    cor = parse_corraw(paths["corraw"])
    prn = parse_print(paths["print"])
    ps = parse_ps(paths["ps"])
    assert table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
    assert "background" in coord["positions"]
    assert cor["n_points"] == 1024
    assert prn["dofull"] is True
    assert ps["has_crude_model_marker"] is False


def test_output_stage_generation_from_computed_case03() -> None:
    paths = generate_outputs_from_computed_case(
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
        OUT / "case03",
    )
    table = parse_table(paths["table"])
    prn = parse_print(paths["print"])
    ps = parse_ps(paths["ps"])
    assert table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
    assert prn["dofull"] is False
    assert ps["has_crude_model_marker"] is True


def test_output_stage_computed_does_not_require_reference_outputs() -> None:
    source = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
    stripped_case = OUT / "case02_inputs_only"
    _copy_case_inputs_only(source, stripped_case)

    paths = generate_outputs_from_computed_case(stripped_case, OUT / "case02_inputs_only_out")
    assert all(path.exists() for path in paths.values())
