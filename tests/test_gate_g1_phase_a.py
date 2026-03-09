from __future__ import annotations

import json
from pathlib import Path

import pytest

from lcmodel_pyport.config.change_log import extract_effective_changes
from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.config.models import ControlConfig
from lcmodel_pyport.core.errors import ValidationError
from lcmodel_pyport.io.raw_reader import compute_raw_scale, read_raw_dataset
from lcmodel_pyport.validation.schemas import validate_control_config

ROOT = Path(__file__).resolve().parents[1]
CASE01_DIR = ROOT / "artifacts" / "step4_exec" / "case01"
CASE02_DIR = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
CHECKPOINTS = ROOT / "tests" / "fixtures" / "lcmodel" / "checkpoints" / "case01"

# For traceability in result reporting:
# - VT-I-001 maps to LCModel.f:70-72, 731-742, 862-867
# - VT-I-002 maps to LCModel.f:2777-2814, 2827-2856
# - VT-S-003 maps to LCModel.f:2072-2132
# - VT-U-N-006 maps to LCModel.f:2827-2839
# - VT-C-004 maps to LCModel.f:10810-10833
# - VT-U-T-001 maps to explicit typed/schema requirement from Step 6 (RQ-016)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_vt_i_001_control_checkpoint_parity_case01() -> None:
    text = (CASE01_DIR / "control.file").read_text(encoding="utf-8")
    cfg = build_control_config(text)
    expected = _load_json(CHECKPOINTS / "CP-CTRL-001.json")

    assert cfg.key == expected["scalars"]["key"]
    assert cfg.nunfil == expected["scalars"]["nunfil"]
    assert cfg.deltat == expected["scalars"]["deltat"]
    assert cfg.hzpppm == expected["scalars"]["hzpppm"]
    assert cfg.dofull is expected["scalars"]["dofull"]
    assert cfg.lps == expected["scalars"]["lps"]
    assert cfg.filbas == expected["paths"]["filbas"]
    assert cfg.filraw == expected["paths"]["filraw"]
    assert cfg.filps == expected["paths"]["filps"]


def test_vt_i_002_raw_stage_checkpoint_parity_case01() -> None:
    dataset = read_raw_dataset(CASE01_DIR / "data.raw", expected_nunfil=1024)
    expected = _load_json(CHECKPOINTS / "CP-RAW-001.json")

    assert dataset.nmid.fmtdat.upper() == expected["nmid"]["fmtdat"].upper()
    assert dataset.nmid.tramp == expected["nmid"]["tramp"]
    assert dataset.nmid.volume == expected["nmid"]["volume"]
    assert dataset.nmid.seqacq is expected["nmid"]["seqacq"]
    assert dataset.nmid.bruker is expected["nmid"]["bruker"]
    assert len(dataset.data) == expected["n_points"]
    assert dataset.data[0].real == pytest.approx(expected["first_sample"]["real"])
    assert dataset.data[0].imag == pytest.approx(expected["first_sample"]["imag"])


def test_vt_s_003_input_change_log_consistency_case02() -> None:
    text = (CASE02_DIR / "control_trace_full.file").read_text(encoding="utf-8")
    changes = extract_effective_changes(text)

    assert "lprint=11" in changes
    assert "lcoord=12" in changes
    assert "ltable=13" in changes
    assert "lcoraw=14" in changes
    assert "filcor='out_trace_full.corraw'" in changes
    assert "filps='out_trace_full.ps'" in changes


def test_vt_u_n_006_raw_scaling_rule() -> None:
    assert compute_raw_scale(1.0, 1.0, 1.0) == pytest.approx(1.0)
    assert compute_raw_scale(1.5, 2.0, 4.0) == pytest.approx(0.75)
    with pytest.raises(ValidationError):
        compute_raw_scale(1.0, 0.0, 1.0)


def test_vt_c_004_corraw_header_contract_case02() -> None:
    dataset = read_raw_dataset(CASE02_DIR / "out_trace_full.corraw", expected_nunfil=1024)
    assert dataset.seqpar is not None
    assert dataset.seqpar.hzpppm == pytest.approx(127.78614, rel=1e-6)
    assert dataset.nmid.fmtdat.strip() != ""
    assert dataset.nmid.seqacq is False
    assert dataset.nmid.bruker is False
    assert len(dataset.data) == 1024


def test_vt_u_t_001_typed_schema_validation_rejects_wrong_types() -> None:
    bad = ControlConfig(
        key=210387309,
        nunfil="1024",  # type: ignore[arg-type]
        deltat=0.0005,
        hzpppm=127.786142,
        filbas="3t.basis",
        filraw="data.raw",
        filps="out.ps",
        dofull=True,
    )
    with pytest.raises(ValidationError):
        validate_control_config(bad)

