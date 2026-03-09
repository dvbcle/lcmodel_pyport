from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.verify.fixtures import load_checksums, load_manifest, verify_checksum

ROOT = Path(__file__).resolve().parents[1]
FIX_ROOT = ROOT / "tests" / "fixtures" / "lcmodel"


def test_manifest_loads_and_contains_case01() -> None:
    manifest = load_manifest(FIX_ROOT / "manifest.json")
    case_ids = [case["id"] for case in manifest["cases"]]
    assert "case01_baseline" in case_ids
    assert "case02_trace_full" in case_ids
    assert "case03_trace_prelim_only" in case_ids


def test_checksum_registry_matches_case01_inputs() -> None:
    checksums = load_checksums(FIX_ROOT / "checksums.sha256")
    assert verify_checksum(
        ROOT,
        "artifacts/step4_exec/case01/control.file",
        checksums["artifacts/step4_exec/case01/control.file"],
    )
    assert verify_checksum(
        ROOT,
        "artifacts/step4_exec/case01/data.raw",
        checksums["artifacts/step4_exec/case01/data.raw"],
    )
    assert verify_checksum(
        ROOT,
        "artifacts/step4_exec/case01/3t.basis",
        checksums["artifacts/step4_exec/case01/3t.basis"],
    )


def test_manifest_expected_outputs_exist_for_trace_cases() -> None:
    manifest = load_manifest(FIX_ROOT / "manifest.json")
    for case in manifest["cases"]:
        outputs = case.get("expected_outputs", {})
        for rel_path in outputs.values():
            assert (ROOT / rel_path).exists()


def test_checksum_registry_matches_trace_case_outputs() -> None:
    checksums = load_checksums(FIX_ROOT / "checksums.sha256")
    for rel_path in (
        "artifacts/step4_exec/case02_trace_full/out_trace_full.print",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.coord",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.table",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.corraw",
        "artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.print",
        "artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.coord",
        "artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.table",
        "artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.corraw",
    ):
        assert verify_checksum(ROOT, rel_path, checksums[rel_path])
