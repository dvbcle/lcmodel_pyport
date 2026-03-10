from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.pipeline.orchestrator import run_case_computed_mode
from lcmodel_pyport.verify.compare import max_abs_delta, rmse
from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / ".tmp" / "strict_parity_gaps"
OUT.mkdir(parents=True, exist_ok=True)

# These are intentionally strict "full-scientific-parity" gates and are expected
# to fail until the port's solver/model behavior reaches Fortran parity.
#
# Fortran traceability:
# - concentration output behavior: LCModel.f:10423-10427
# - coord vector output behavior: LCModel.f:10775-10787


def _run_case(case_name: str) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    case_dir = ROOT / "artifacts" / "step4_exec" / case_name
    result = run_case_computed_mode(case_dir, OUT)
    py_table = parse_table(result.output_paths["table"])
    py_coord = parse_coord(result.output_paths["coord"])
    ref_table = parse_table(next(case_dir.glob("*.table")))
    ref_coord = parse_coord(next(case_dir.glob("*.coord")))
    return py_table, py_coord, ref_table, ref_coord


def test_strict_case02_concentration_identity_and_values() -> None:
    py_table, _py_coord, ref_table, _ref_coord = _run_case("case02_trace_full")
    # Full parity gate: concentration rows must match exactly by metabolite/value/%SD/ratio.
    assert py_table["concentration_details"] == ref_table["concentration_details"]


def test_strict_case03_prelim_metabolite_subset_and_values() -> None:
    py_table, _py_coord, ref_table, _ref_coord = _run_case("case03_trace_prelim_only")
    # Full parity gate: prelim-only concentration subset must match Fortran exactly.
    assert py_table["concentration_details"] == ref_table["concentration_details"]


def test_strict_case02_coord_vector_tolerances() -> None:
    _py_table, py_coord, _ref_table, ref_coord = _run_case("case02_trace_full")
    # Full parity gate: tighten well beyond current VT-N profile.
    # Expected to fail until solver + phase/fit modeling are fully ported.
    for key in ("ppm_axis", "phased_data", "fit", "background"):
        rv = [float(x) for x in ref_coord["vectors"][key]]
        pv = [float(x) for x in py_coord["vectors"][key]]
        assert rmse(rv, pv) <= 1e-6
        assert max_abs_delta(rv, pv) <= 1e-5
