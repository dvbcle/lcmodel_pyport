"""Evidence-grade parity run helpers for external dataset fixtures."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.fit.fullfit_engine import run_fullfit_computed
from lcmodel_pyport.fit.prelim_engine import run_prelim_computed
from lcmodel_pyport.io.basis_reader import read_basis_dataset
from lcmodel_pyport.io.raw_reader import read_raw_dataset
from lcmodel_pyport.pipeline.orchestrator import run_case_computed_mode
from lcmodel_pyport.verify.compare import close_scalar, max_abs_delta, rmse
from lcmodel_pyport.verify.fixtures import load_checksums, verify_checksum
from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_corraw import parse_corraw
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_ps import parse_ps
from lcmodel_pyport.verify.ps_inputs import build_ps_input_checkpoint, checkpoint_to_dict
from lcmodel_pyport.verify.parsers_table import parse_table
from lcmodel_pyport.verify.tolerances import ToleranceProfile


@dataclass(frozen=True)
class StageEvidence:
    stage: str
    status: str  # pass | fail | not_implemented
    detail: str
    checks: dict[str, Any]
    fortran_refs: list[str]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_pass(stage: str, detail: str, checks: dict[str, Any], refs: list[str]) -> StageEvidence:
    return StageEvidence(stage=stage, status="pass", detail=detail, checks=checks, fortran_refs=refs)


def _stage_fail(stage: str, detail: str, checks: dict[str, Any], refs: list[str]) -> StageEvidence:
    return StageEvidence(stage=stage, status="fail", detail=detail, checks=checks, fortran_refs=refs)


def _stage_not_impl(stage: str, detail: str, refs: list[str]) -> StageEvidence:
    return StageEvidence(
        stage=stage,
        status="not_implemented",
        detail=detail,
        checks={},
        fortran_refs=refs,
    )


def run_external_dataset_evidence(root: Path) -> dict[str, Any]:
    checksums = load_checksums(root / "tests" / "fixtures" / "lcmodel" / "checksums.sha256")
    cp_root = root / "tests" / "fixtures" / "lcmodel" / "checkpoints"

    stages: list[StageEvidence] = []
    tol = ToleranceProfile(float_abs=1e-4, float_rel=1e-3, vector_rmse=5e-3, vector_max_abs=2e-2)

    checksum_paths = [
        "artifacts/step4_exec/case02_trace_full/control_trace_full.file",
        "artifacts/step4_exec/case02_trace_full/data.raw",
        "artifacts/step4_exec/case02_trace_full/3t.basis",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.print",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.coord",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.table",
        "artifacts/step4_exec/case02_trace_full/out_trace_full.corraw",
        "artifacts/step4_exec/case03_trace_prelim_only/control_trace_prelim.file",
        "artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.print",
        "artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.table",
    ]
    checksum_ok = all(verify_checksum(root, p, checksums[p]) for p in checksum_paths)
    stages.append(
        _stage_pass(
            "fixture_integrity",
            "All required external-dataset fixture checksums matched.",
            {"files_checked": len(checksum_paths)},
            ["docs/step7_test_harness_tdd_outline.md:436"],
        )
        if checksum_ok
        else _stage_fail(
            "fixture_integrity",
            "Fixture checksum mismatch detected.",
            {"files_checked": len(checksum_paths)},
            ["docs/step7_test_harness_tdd_outline.md:436"],
        )
    )

    try:
        cfg_full = build_control_config(
            (root / "artifacts" / "step4_exec" / "case02_trace_full" / "control_trace_full.file").read_text(
                encoding="utf-8"
            )
        )
        cfg_pre = build_control_config(
            (root / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "control_trace_prelim.file").read_text(
                encoding="utf-8"
            )
        )
        stages.append(
            _stage_pass(
                "control_stage",
                "Control parsing parity for full and prelim controls.",
                {"full_dofull": cfg_full.dofull, "prelim_dofull": cfg_pre.dofull},
                ["LCModel.f:70-72", "LCModel.f:731-742", "LCModel.f:862-867"],
            )
        )
    except Exception as exc:  # pragma: no cover - surfaced in evidence report
        stages.append(
            _stage_fail(
                "control_stage",
                f"Control stage failed: {exc}",
                {},
                ["LCModel.f:70-72", "LCModel.f:731-742", "LCModel.f:862-867"],
            )
        )

    try:
        raw = read_raw_dataset(root / "artifacts" / "step4_exec" / "case01" / "data.raw", expected_nunfil=1024)
        cp_raw = _load_json(cp_root / "case01" / "CP-RAW-001.json")
        ok = (
            len(raw.data) == cp_raw["n_points"]
            and abs(raw.data[0].real - cp_raw["first_sample"]["real"]) <= 1e-6
            and abs(raw.data[0].imag - cp_raw["first_sample"]["imag"]) <= 1e-6
        )
        stages.append(
            _stage_pass(
                "raw_stage",
                "RAW parse/scaling contract parity against checkpoint.",
                {"n_points": len(raw.data), "first_real": raw.data[0].real, "first_imag": raw.data[0].imag},
                ["LCModel.f:2777-2814", "LCModel.f:2827-2856"],
            )
            if ok
            else _stage_fail(
                "raw_stage",
                "RAW parity mismatch against checkpoint.",
                {"n_points": len(raw.data), "first_real": raw.data[0].real, "first_imag": raw.data[0].imag},
                ["LCModel.f:2777-2814", "LCModel.f:2827-2856"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(
            _stage_fail("raw_stage", f"RAW stage failed: {exc}", {}, ["LCModel.f:2777-2814", "LCModel.f:2827-2856"])
        )

    try:
        basis = read_basis_dataset(root / "artifacts" / "step4_exec" / "case02_trace_full" / "3t.basis")
        cp_basis = _load_json(cp_root / "case02" / "CP-BASIS-001.json")
        p = parse_print(root / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.print")
        ok = (
            basis.idbasi == cp_basis["scalars"]["basis_set_id"]
            and len(basis.metabolite_ids) == cp_basis["scalars"]["basis_file_entry_count"]
            and p["preliminary_metabolites"] == cp_basis["vectors"]["preliminary_metabolites"]
        )
        stages.append(
            _stage_pass(
                "basis_stage",
                "Basis selection parity for external dataset.",
                {"basis_set_id": basis.idbasi, "basis_entries": len(basis.metabolite_ids)},
                ["LCModel.f:3216-3238", "LCModel.f:3297-3306"],
            )
            if ok
            else _stage_fail(
                "basis_stage",
                "Basis stage mismatch against checkpoint.",
                {"basis_set_id": basis.idbasi, "basis_entries": len(basis.metabolite_ids)},
                ["LCModel.f:3216-3238", "LCModel.f:3297-3306"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(_stage_fail("basis_stage", f"Basis stage failed: {exc}", {}, ["LCModel.f:3216-3238"]))

    try:
        pre_cfg = build_control_config(
            (root / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "control_trace_prelim.file").read_text(
                encoding="utf-8"
            )
        )
        pre_raw = read_raw_dataset(
            root / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "data.raw",
            expected_nunfil=pre_cfg.nunfil,
        )
        pre_basis = read_basis_dataset(root / "artifacts" / "step4_exec" / "case03_trace_prelim_only" / "3t.basis")
        pre_cp = run_prelim_computed(pre_cfg, pre_raw, pre_basis)
        cp_pre = _load_json(cp_root / "case03" / "CP-PRELIM-001.json")
        ok = (
            pre_cp.dofull is False
            and pre_cp.best_shift_points == cp_pre["scalars"]["best_shift_points"]
            and close_scalar(pre_cp.best_shift_ppm, cp_pre["scalars"]["best_shift_ppm"], abs_tol=1e-5, rel_tol=1e-3)
            and close_scalar(pre_cp.rephase_deg, cp_pre["scalars"]["rephase_deg"], abs_tol=0.2, rel_tol=1e-3)
            and close_scalar(pre_cp.rephase_degppm, cp_pre["scalars"]["rephase_degppm"], abs_tol=0.2, rel_tol=1e-3)
            and close_scalar(
                pre_cp.gaussian_fwhm_ppm,
                cp_pre["scalars"]["gaussian_fwhm_ppm"],
                abs_tol=1e-5,
                rel_tol=1e-3,
            )
        )
        stages.append(
            _stage_pass(
                "prelim_stage",
                "Preliminary stage checkpoint parity from computed prelim engine.",
                {"best_shift_points": pre_cp.best_shift_points, "dofull": pre_cp.dofull},
                ["LCModel.f:331-346", "LCModel.f:5441-5444", "LCModel.f:6962-7025"],
            )
            if ok
            else _stage_fail(
                "prelim_stage",
                "Preliminary stage mismatch against checkpoint.",
                {"best_shift_points": pre_cp.best_shift_points, "dofull": pre_cp.dofull},
                ["LCModel.f:331-346", "LCModel.f:5441-5444", "LCModel.f:6962-7025"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(_stage_fail("prelim_stage", f"Prelim stage failed: {exc}", {}, ["LCModel.f:331-346"]))

    try:
        full_cfg = build_control_config(
            (root / "artifacts" / "step4_exec" / "case02_trace_full" / "control_trace_full.file").read_text(
                encoding="utf-8"
            )
        )
        full_raw = read_raw_dataset(
            root / "artifacts" / "step4_exec" / "case02_trace_full" / "data.raw",
            expected_nunfil=full_cfg.nunfil,
        )
        full_basis = read_basis_dataset(root / "artifacts" / "step4_exec" / "case02_trace_full" / "3t.basis")
        full_prelim = run_prelim_computed(full_cfg, full_raw, full_basis)
        cp = run_fullfit_computed(
            full_cfg,
            full_raw,
            full_basis,
            full_prelim,
        )
        cp_full = _load_json(cp_root / "case02" / "CP-FULL-001.json")
        ok = (
            cp.phase_pair_count == cp_full["scalars"]["phase_pair_count"]
            and cp.reference_solution_count == cp_full["scalars"]["reference_solution_count"]
            and close_scalar(cp.prelim_alpha_b, cp_full["scalars"]["prelim_alpha_b"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.prelim_alpha_s, cp_full["scalars"]["prelim_alpha_s"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.final_alpha_b, cp_full["scalars"]["final_alpha_b"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.final_alpha_s, cp_full["scalars"]["final_alpha_s"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.fwhm_ppm, cp_full["scalars"]["fwhm_ppm"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.sn, cp_full["scalars"]["sn"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.data_shift_ppm, cp_full["scalars"]["data_shift_ppm"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(cp.phase0_deg, cp_full["scalars"]["phase0_deg"], abs_tol=1e-9, rel_tol=1e-6)
            and close_scalar(
                cp.phase1_deg_per_ppm,
                cp_full["scalars"]["phase1_deg_per_ppm"],
                abs_tol=1e-9,
                rel_tol=1e-6,
            )
            and cp.concentration_rows == cp_full["scalars"]["concentration_rows"]
        )
        stages.append(
            _stage_pass(
                "fullfit_stage",
                "Fullfit checkpoint parity from computed fullfit engine.",
                {"phase_pair_count": cp.phase_pair_count, "alpha_b": cp.final_alpha_b, "alpha_s": cp.final_alpha_s},
                ["LCModel.f:352-356", "LCModel.f:7216-7252", "LCModel.f:7430-7433", "LCModel.f:10008-10056"],
            )
            if ok
            else _stage_fail(
                "fullfit_stage",
                "Fullfit checkpoint mismatch.",
                {"phase_pair_count": cp.phase_pair_count, "alpha_b": cp.final_alpha_b, "alpha_s": cp.final_alpha_s},
                ["LCModel.f:352-356", "LCModel.f:7216-7252", "LCModel.f:7430-7433", "LCModel.f:10008-10056"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(_stage_fail("fullfit_stage", f"Fullfit stage failed: {exc}", {}, ["LCModel.f:7216-7252"]))

    try:
        table = parse_table(root / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.table")
        coord = parse_coord(root / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.coord")
        cor = parse_corraw(root / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.corraw")
        prn = parse_print(root / "artifacts" / "step4_exec" / "case02_trace_full" / "out_trace_full.print")
        ok = (
            table["sections_order"] == ["$$CONC", "$$MISC", "$$DIAG", "$$INPU"]
            and "background" in coord["positions"]
            and cor["n_points"] == 1024
            and prn["dofull"] is True
        )
        stages.append(
            _stage_pass(
                "output_contract_stage",
                "Output contracts parse and match required structure/markers.",
                {"table_sections": table["sections_order"], "coord_markers": list(coord["positions"].keys())},
                ["LCModel.f:10423-10427", "LCModel.f:10775-10787", "LCModel.f:10810-10833"],
            )
            if ok
            else _stage_fail(
                "output_contract_stage",
                "Output contract mismatch.",
                {"table_sections": table["sections_order"], "coord_markers": list(coord["positions"].keys())},
                ["LCModel.f:10423-10427", "LCModel.f:10775-10787", "LCModel.f:10810-10833"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(
            _stage_fail("output_contract_stage", f"Output contract stage failed: {exc}", {}, ["LCModel.f:10423-10427"])
        )

    generated_dir = root / "tests" / ".tmp" / "generated_external_cases"
    try:
        orchestration_full = run_case_computed_mode(
            root / "artifacts" / "step4_exec" / "case02_trace_full",
            generated_dir,
        )
        orchestration_prelim = run_case_computed_mode(
            root / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
            generated_dir,
        )
        generated = {
            "case02": orchestration_full.output_paths,
            "case03": orchestration_prelim.output_paths,
        }
        files_exist = (
            all(path.exists() for path in orchestration_full.output_paths.values())
            and orchestration_full.output_generated
            and all(path.exists() for path in orchestration_prelim.output_paths.values())
            and orchestration_prelim.output_generated
        )
        stages.append(
            _stage_pass(
                "python_pipeline_e2e_generation",
                "Python computed-mode orchestration produced all expected files.",
                {
                    "generated_files": {
                        "case02": {k: str(v) for k, v in orchestration_full.output_paths.items()},
                        "case03": {k: str(v) for k, v in orchestration_prelim.output_paths.items()},
                    },
                    "case02_dofull": orchestration_full.dofull,
                    "case02_fullfit_loaded": orchestration_full.fullfit_loaded,
                    "case02_generation_mode": orchestration_full.generation_mode,
                    "case03_dofull": orchestration_prelim.dofull,
                    "case03_fullfit_loaded": orchestration_prelim.fullfit_loaded,
                    "case03_generation_mode": orchestration_prelim.generation_mode,
                },
                ["docs/step8_python_architecture_proposal.md:294-296"],
            )
            if files_exist
            else _stage_fail(
                "python_pipeline_e2e_generation",
                "Generated outputs missing expected files.",
                {
                    "generated_files": {
                        "case02": {k: str(v) for k, v in orchestration_full.output_paths.items()},
                        "case03": {k: str(v) for k, v in orchestration_prelim.output_paths.items()},
                    },
                    "case02_dofull": orchestration_full.dofull,
                    "case02_fullfit_loaded": orchestration_full.fullfit_loaded,
                    "case02_generation_mode": orchestration_full.generation_mode,
                    "case03_dofull": orchestration_prelim.dofull,
                    "case03_fullfit_loaded": orchestration_prelim.fullfit_loaded,
                    "case03_generation_mode": orchestration_prelim.generation_mode,
                },
                ["docs/step8_python_architecture_proposal.md:294-296"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(
            _stage_fail(
                "python_pipeline_e2e_generation",
                f"Python output-stage generation failed: {exc}",
                {},
                ["docs/step8_python_architecture_proposal.md:294-296"],
            )
        )
        generated = {}

    try:
        if not generated:
            raise RuntimeError("generated outputs unavailable")
        ps_input_checks: dict[str, Any] = {}
        ps_input_ok = True
        for case_id, ref_dir, py_paths, cp_path in (
            (
                "case02",
                root / "artifacts" / "step4_exec" / "case02_trace_full",
                generated["case02"],
                cp_root / "case02" / "CP-PS-INPUT-001.json",
            ),
            (
                "case03",
                root / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
                generated["case03"],
                cp_root / "case03" / "CP-PS-INPUT-001.json",
            ),
        ):
            cp_expected = _load_json(cp_path)["scalars"]
            cp_ref = checkpoint_to_dict(
                build_ps_input_checkpoint(
                    next(ref_dir.glob("*.coord")),
                    next(ref_dir.glob("*.print")),
                    next(ref_dir.glob("*.ps")),
                )
            )
            cp_py = checkpoint_to_dict(
                build_ps_input_checkpoint(
                    py_paths["coord"],
                    py_paths["print"],
                    py_paths["ps"],
                )
            )
            case_checks = {
                "reference_matches_checkpoint": (
                    cp_ref["ny"] == cp_expected["ny"]
                    and cp_ref["dofull"] == cp_expected["dofull"]
                    and cp_ref["has_crude_model_marker"] == cp_expected["has_crude_model_marker"]
                ),
                "generated_branch_match": (
                    cp_py["dofull"] == cp_ref["dofull"]
                    and cp_py["has_crude_model_marker"] == cp_ref["has_crude_model_marker"]
                ),
                "generated_vector_heads_rmse": {
                    "phased": rmse(cp_py["phased_head3"], cp_ref["phased_head3"]),
                    "fit": rmse(cp_py["fit_head3"], cp_ref["fit_head3"]),
                    "background": rmse(cp_py["background_head3"], cp_ref["background_head3"]),
                },
            }
            case_checks["generated_vector_heads_within_tolerance"] = all(
                v <= tol.vector_rmse for v in case_checks["generated_vector_heads_rmse"].values()
            )
            case_checks["overall_case_ok"] = (
                case_checks["reference_matches_checkpoint"]
                and case_checks["generated_branch_match"]
                and case_checks["generated_vector_heads_within_tolerance"]
            )
            ps_input_checks[case_id] = case_checks
            if not case_checks["overall_case_ok"]:
                ps_input_ok = False

        stages.append(
            _stage_pass(
                "ps_input_parity_stage",
                "PS input intermediates match checkpoints/reference for both external branches.",
                {"cases": ps_input_checks},
                ["LCModel.f:10775-10787", "LCModel.f:11476-11483"],
            )
            if ps_input_ok
            else _stage_fail(
                "ps_input_parity_stage",
                "PS input intermediate parity failed for one or more branches.",
                {"cases": ps_input_checks},
                ["LCModel.f:10775-10787", "LCModel.f:11476-11483"],
            )
        )

        checks: dict[str, Any] = {}
        overall_ok = True
        checks_by_case: dict[str, Any] = {}

        for case_id, ref_dir, py_paths in (
            (
                "case02",
                root / "artifacts" / "step4_exec" / "case02_trace_full",
                generated["case02"],
            ),
            (
                "case03",
                root / "artifacts" / "step4_exec" / "case03_trace_prelim_only",
                generated["case03"],
            ),
        ):
            ref_table = parse_table(next(ref_dir.glob("*.table")))
            py_table = parse_table(py_paths["table"])
            ref_coord = parse_coord(next(ref_dir.glob("*.coord")))
            py_coord = parse_coord(py_paths["coord"])
            ref_print = parse_print(next(ref_dir.glob("*.print")))
            py_print = parse_print(py_paths["print"])
            ref_cor = parse_corraw(next(ref_dir.glob("*.corraw")))
            py_cor = parse_corraw(py_paths["corraw"])
            ref_ps = parse_ps(next(ref_dir.glob("*.ps")))
            py_ps = parse_ps(py_paths["ps"]) if "ps" in py_paths else {"has_crude_model_marker": None}

            case_checks: dict[str, Any] = {}
            case_checks["table_sections_match"] = ref_table["sections_order"] == py_table["sections_order"]
            case_checks["concentration_rows_match"] = ref_table["concentration_rows"] == py_table["concentration_rows"]
            case_checks["print_dofull_match"] = ref_print["dofull"] == py_print["dofull"]
            case_checks["print_phase_pair_count_match"] = ref_print["phase_pair_count"] == py_print["phase_pair_count"]
            case_checks["corraw_n_points_match"] = ref_cor["n_points"] == py_cor["n_points"]
            case_checks["ps_crude_marker_match"] = (
                ref_ps["has_crude_model_marker"] == py_ps["has_crude_model_marker"]
            )

            scalar_ok = True
            scalar_deltas: dict[str, float] = {}
            for key in ("fwhm_ppm", "sn", "data_shift_ppm", "phase0_deg", "phase1_deg_per_ppm", "alpha_b", "alpha_s"):
                rv = float(ref_table["misc_metrics"][key])
                pv = float(py_table["misc_metrics"][key])
                scalar_deltas[key] = abs(rv - pv)
                if not close_scalar(pv, rv, abs_tol=tol.float_abs, rel_tol=tol.float_rel):
                    scalar_ok = False
            case_checks["misc_scalar_deltas"] = scalar_deltas
            case_checks["misc_scalars_within_tolerance"] = scalar_ok

            vector_ok = True
            vector_metrics: dict[str, dict[str, float]] = {}
            for key in ("ppm_axis", "phased_data", "fit", "background"):
                rv = [float(x) for x in ref_coord["vectors"][key]]
                pv = [float(x) for x in py_coord["vectors"][key]]
                vrmse = rmse(rv, pv)
                vmax = max_abs_delta(rv, pv)
                vector_metrics[key] = {"rmse": vrmse, "max_abs": vmax}
                if vrmse > tol.vector_rmse or vmax > tol.vector_max_abs:
                    vector_ok = False
            case_checks["vector_metrics"] = vector_metrics
            case_checks["vectors_within_tolerance"] = vector_ok
            case_checks["overall_case_ok"] = (
                case_checks["table_sections_match"]
                and case_checks["concentration_rows_match"]
                and case_checks["print_dofull_match"]
                and case_checks["print_phase_pair_count_match"]
                and case_checks["corraw_n_points_match"]
                and case_checks["ps_crude_marker_match"]
                and case_checks["misc_scalars_within_tolerance"]
                and case_checks["vectors_within_tolerance"]
            )
            checks_by_case[case_id] = case_checks
            if not case_checks["overall_case_ok"]:
                overall_ok = False
        checks["cases"] = checks_by_case
        stages.append(
            _stage_pass(
                "output_numeric_regression_stage",
                "Generated outputs match reference contracts and numeric tolerances.",
                checks,
                ["docs/step7_test_harness_tdd_outline.md:232-239"],
            )
            if overall_ok
            else _stage_fail(
                "output_numeric_regression_stage",
                "Generated outputs failed contract or numeric tolerance checks.",
                checks,
                ["docs/step7_test_harness_tdd_outline.md:232-239"],
            )
        )
    except Exception as exc:  # pragma: no cover
        stages.append(
            _stage_fail(
                "output_numeric_regression_stage",
                f"Numeric regression stage failed: {exc}",
                {},
                ["docs/step7_test_harness_tdd_outline.md:232-239"],
            )
        )

    out = {
        "evidence_id": "VT-E2E-EVID-001",
        "dataset": "external_repo_test_lcm",
        "stages": [asdict(s) for s in stages],
    }
    out["summary"] = {
        "pass": sum(1 for s in stages if s.status == "pass"),
        "fail": sum(1 for s in stages if s.status == "fail"),
        "not_implemented": sum(1 for s in stages if s.status == "not_implemented"),
    }
    return out
