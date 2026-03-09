from __future__ import annotations

import json
from pathlib import Path

from lcmodel_pyport.verify.evidence import run_external_dataset_evidence

ROOT = Path(__file__).resolve().parents[1]


def test_vt_e2e_evid_001_external_dataset() -> None:
    evidence = run_external_dataset_evidence(ROOT)
    out_dir = ROOT / "tests" / ".tmp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "evidence_external_dataset.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    assert evidence["evidence_id"] == "VT-E2E-EVID-001"
    assert evidence["summary"]["fail"] == 0
    assert evidence["summary"]["not_implemented"] == 0
    assert evidence["summary"]["pass"] >= 8
