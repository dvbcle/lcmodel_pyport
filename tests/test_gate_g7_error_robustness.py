from __future__ import annotations

from pathlib import Path

import pytest

from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.core.errors import ControlParseError
from lcmodel_pyport.pipeline.orchestrator import run_case_reference_mode
from lcmodel_pyport.pipeline.output_stage import generate_outputs_from_reference_case

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tests" / ".tmp" / "gate_g7_errors"
TMP.mkdir(parents=True, exist_ok=True)

# Traceability:
# - VT-U-T-002 integer control field enforcement (Step 6 RQ-016)
# - VT-U-E-001/002/003 error-path behaviors for missing inputs/output-stage dependencies


def test_vt_u_t_002_reject_non_integer_control_fields() -> None:
    text = """
$LCMODL
nunfil=1024.5
deltat=5e-04
hzpppm=127.786142
filbas='3t.basis'
filraw='data.raw'
filps='out.ps'
$END
""".strip()
    with pytest.raises(ControlParseError):
        build_control_config(text)


def test_vt_u_e_001_orchestrator_missing_control_file() -> None:
    case_dir = TMP / "missing_control"
    case_dir.mkdir(parents=True, exist_ok=True)
    with pytest.raises(FileNotFoundError):
        run_case_reference_mode(case_dir, TMP / "out_missing_control")


def test_vt_u_e_002_output_stage_missing_reference_files() -> None:
    case_dir = TMP / "missing_refs"
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "control.file").write_text(
        "\n".join(
            [
                "$LCMODL",
                "nunfil=1024",
                "deltat=5e-04",
                "hzpppm=127.786142",
                "filbas='3t.basis'",
                "filraw='data.raw'",
                "filps='out.ps'",
                "filpri='out.print'",
                "filcoo='out.coord'",
                "filtab='out.table'",
                "filcor='out.corraw'",
                "$END",
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError):
        generate_outputs_from_reference_case(case_dir, TMP / "out_missing_refs")
