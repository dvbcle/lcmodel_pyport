from __future__ import annotations

import cmath
from pathlib import Path

import numpy as np

from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.config.models import RawDataset
from lcmodel_pyport.fit.fullfit_engine import run_fullfit_computed
from lcmodel_pyport.fit.prelim_engine import run_prelim_computed
from lcmodel_pyport.io.basis_reader import read_basis_dataset
from lcmodel_pyport.io.raw_reader import read_raw_dataset

ROOT = Path(__file__).resolve().parents[1]


def _case02_inputs() -> tuple[object, RawDataset, object]:
    case = ROOT / "artifacts" / "step4_exec" / "case02_trace_full"
    cfg = build_control_config((case / "control_trace_full.file").read_text(encoding="utf-8"))
    raw = read_raw_dataset(case / "data.raw", expected_nunfil=cfg.nunfil)
    basis = read_basis_dataset(case / "3t.basis")
    return cfg, raw, basis


def test_prelim_best_shift_tracks_frequency_shift_direction() -> None:
    cfg, raw, basis = _case02_inputs()
    base = run_prelim_computed(cfg, raw, basis)

    n = cfg.nunfil
    plus_data = [z * cmath.exp(2j * np.pi * 2 * i / n) for i, z in enumerate(raw.data)]
    minus_data = [z * cmath.exp(2j * np.pi * (-2) * i / n) for i, z in enumerate(raw.data)]
    plus = run_prelim_computed(cfg, RawDataset(seqpar=raw.seqpar, nmid=raw.nmid, data=plus_data), basis)
    minus = run_prelim_computed(cfg, RawDataset(seqpar=raw.seqpar, nmid=raw.nmid, data=minus_data), basis)

    assert plus.best_shift_points < base.best_shift_points
    assert minus.best_shift_points > base.best_shift_points


def test_fullfit_computed_sn_tracks_noise_level() -> None:
    cfg, raw, basis = _case02_inputs()
    prelim_clean = run_prelim_computed(cfg, raw, basis)
    full_clean = run_fullfit_computed(cfg, raw, basis, prelim_clean)

    rng = np.random.default_rng(12345)
    noisy_data = [
        z + complex(rng.normal(scale=5e-4), rng.normal(scale=5e-4)) for z in raw.data
    ]
    noisy_raw = RawDataset(seqpar=raw.seqpar, nmid=raw.nmid, data=noisy_data)
    prelim_noisy = run_prelim_computed(cfg, noisy_raw, basis)
    full_noisy = run_fullfit_computed(cfg, noisy_raw, basis, prelim_noisy)

    assert full_noisy.sn < full_clean.sn
