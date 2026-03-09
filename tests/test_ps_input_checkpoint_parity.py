from __future__ import annotations

import json
from pathlib import Path

import pytest

from lcmodel_pyport.verify.ps_inputs import build_ps_input_checkpoint, checkpoint_to_dict

ROOT = Path(__file__).resolve().parents[1]

# Traceability:
# - Intermediate PS input parity from LCModel.f output vectors: 10775-10787
# - Prelim-only CRUDE MODEL branch marker in PS: 11476-11483


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_close(actual: dict, expected: dict) -> None:
    assert actual["ny"] == expected["ny"]
    assert actual["dofull"] is expected["dofull"]
    assert actual["has_crude_model_marker"] is expected["has_crude_model_marker"]
    for key in (
        "ppm_first",
        "ppm_last",
        "phased_min",
        "phased_max",
        "fit_min",
        "fit_max",
        "background_min",
        "background_max",
    ):
        assert actual[key] == pytest.approx(expected[key], rel=1e-8, abs=1e-9)
    for key in ("phased_head3", "fit_head3", "background_head3"):
        assert len(actual[key]) == len(expected[key])
        for a, e in zip(actual[key], expected[key]):
            assert a == pytest.approx(e, rel=1e-8, abs=1e-9)


def test_cp_ps_input_case02() -> None:
    cp = build_ps_input_checkpoint(
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.coord",
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.print",
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.ps",
    )
    expected = _load(ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case02" / "CP-PS-INPUT-001.json")
    _assert_close(checkpoint_to_dict(cp), expected["scalars"])


def test_cp_ps_input_case03() -> None:
    cp = build_ps_input_checkpoint(
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "out_trace_prelim.coord",
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "out_trace_prelim.print",
        ROOT / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "out_trace_prelim.ps",
    )
    expected = _load(ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case03" / "CP-PS-INPUT-001.json")
    _assert_close(checkpoint_to_dict(cp), expected["scalars"])
