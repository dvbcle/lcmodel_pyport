from __future__ import annotations

from pathlib import Path

import numpy as np

from lcmodel_pyport.io.basis_reader import read_basis_dataset
from lcmodel_pyport.fit.fullfit_engine import solve_base_amplitudes
from lcmodel_pyport.fit.prelim_engine import build_analysis_vectors
from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.io.raw_reader import read_raw_dataset
from lcmodel_pyport.pipeline.output_stage import generate_outputs_from_computed_case
from lcmodel_pyport.verify.parsers_table import parse_table

ROOT = Path(__file__).resolve().parents[1]


def test_basis_payload_entries_have_expected_shape() -> None:
    basis = read_basis_dataset(ROOT / "artifacts" / "step4_exec" / "case02_trace_full" / "3t.basis")
    assert len(basis.entries) == len(basis.metabolite_ids)
    assert len(basis.entries) > 0
    assert all(len(entry.data) == basis.ndatab for entry in basis.entries)
    assert any(np.linalg.norm(np.asarray(entry.data, dtype=np.complex128)) > 0 for entry in basis.entries)


def test_computed_concentrations_are_nonnegative_from_solver_path() -> None:
    out = ROOT / "tests" / ".tmp" / "gate_g3_basis_payloads"
    paths = generate_outputs_from_computed_case(
        ROOT / "artifacts" / "step4_exec" / "case02_trace_full",
        out,
    )
    table = parse_table(paths["table"])
    assert table["concentration_rows"] == 35
    assert all(float(row["conc"]) >= 0 for row in table["concentration_details"])


def test_fit_layer_base_amplitude_solver_contract() -> None:
    case = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
    cfg = build_control_config((case / "control_trace_full.file").read_text(encoding="utf-8"))
    raw = read_raw_dataset(case / "data.raw", expected_nunfil=cfg.nunfil)
    basis = read_basis_dataset(case / "3t.basis")
    _axis, phased, _fit, _bg, _sn = build_analysis_vectors(cfg, raw)

    amps = solve_base_amplitudes(phased, basis)
    assert amps.shape[0] == len(basis.entries)
    assert np.all(amps >= 0.0)
