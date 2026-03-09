from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.verify.fixtures import load_checksums, load_manifest, verify_checksum

ROOT = Path(__file__).resolve().parents[1]
FIX_ROOT = ROOT / "tests" / "fixtures" / "lcmodel"


def test_manifest_loads_and_contains_case01() -> None:
    manifest = load_manifest(FIX_ROOT / "manifest.json")
    case_ids = [case["id"] for case in manifest["cases"]]
    assert "case01_baseline" in case_ids


def test_checksum_registry_matches_case01_inputs() -> None:
    checksums = load_checksums(FIX_ROOT / "checksums.sha256")
    assert verify_checksum(ROOT, "artifacts/step4_exec/case01/control.file", checksums["artifacts/step4_exec/case01/control.file"])
    assert verify_checksum(ROOT, "artifacts/step4_exec/case01/data.raw", checksums["artifacts/step4_exec/case01/data.raw"])
    assert verify_checksum(ROOT, "artifacts/step4_exec/case01/3t.basis", checksums["artifacts/step4_exec/case01/3t.basis"])

