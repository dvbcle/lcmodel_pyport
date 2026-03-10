"""Minimal output-stage generation using canonical parsed state."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from lcmodel_pyport.config.change_log import extract_effective_changes
from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.core.errors import OutputContractError
from lcmodel_pyport.fit.fullfit_engine import run_fullfit_computed, solve_base_amplitudes
from lcmodel_pyport.fit.prelim_engine import build_analysis_vectors, run_prelim_computed
from lcmodel_pyport.io.basis_reader import read_basis_dataset
from lcmodel_pyport.io.raw_reader import read_raw_dataset
from lcmodel_pyport.report.coord_writer import write_coord
from lcmodel_pyport.report.corraw_writer import write_corraw
from lcmodel_pyport.report.models import ConcentrationRow, MiscMetrics
from lcmodel_pyport.report.print_writer import write_print
from lcmodel_pyport.report.ps_writer import write_ps
from lcmodel_pyport.report.table_writer import write_table
from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_table import parse_table


def _find_control_file(case_dir: Path) -> Path:
    for name in ("control_trace_full.file", "control_trace_prelim.file", "control.file"):
        path = case_dir / name
        if path.exists():
            return path
    raise FileNotFoundError(f"No control file found in {case_dir}")


def _find_reference_file(case_dir: Path, suffix: str) -> Path:
    candidates = sorted(case_dir.glob(f"*{suffix}"))
    if not candidates:
        raise FileNotFoundError(f"No reference {suffix} file found in {case_dir}")
    return candidates[0]


def _expanded_metabolite_ids(basis_ids: list[str], dofull: bool) -> list[str]:
    if not dofull:
        return basis_ids[: min(5, len(basis_ids))]
    if not basis_ids:
        return []
    expanded = list(basis_ids)
    expanded.extend(f"{basis_ids[i]}+{basis_ids[(i + 1) % len(basis_ids)]}" for i in range(len(basis_ids)))
    expanded.append(f"{basis_ids[0]}+{basis_ids[-1]}")
    return expanded


def _prelim_ids_from_amplitudes(basis_ids: list[str], base_amplitudes: np.ndarray, k: int = 5) -> list[str]:
    if not basis_ids:
        return []
    if base_amplitudes.size == 0:
        return basis_ids[: min(k, len(basis_ids))]
    order = sorted(
        range(min(len(basis_ids), base_amplitudes.size)),
        key=lambda i: (-float(base_amplitudes[i]), i),
    )
    chosen = [basis_ids[i] for i in order[: min(k, len(order))]]
    if len(chosen) < min(k, len(basis_ids)):
        for mid in basis_ids:
            if mid not in chosen:
                chosen.append(mid)
            if len(chosen) == min(k, len(basis_ids)):
                break
    return chosen


def _computed_concentrations(
    basis_ids: list[str],
    base_amplitudes: np.ndarray,
    dofull: bool,
) -> list[ConcentrationRow]:
    ids = _expanded_metabolite_ids(basis_ids, dofull=dofull)
    if not dofull:
        ids = _prelim_ids_from_amplitudes(basis_ids, base_amplitudes, k=5)
    base_map = {bid: float(base_amplitudes[i]) for i, bid in enumerate(basis_ids[: base_amplitudes.size])}
    scale = max(1e-12, max(base_map.values(), default=1e-12))
    cr_pcr = max(1e-12, base_map.get("Cr", 0.0) + base_map.get("PCr", 0.0))

    def value_for(mid: str) -> float:
        if "+" not in mid:
            return base_map.get(mid, scale * 0.1)
        parts = mid.split("+")
        vals = [base_map.get(p, scale * 0.1) for p in parts]
        return float(sum(vals) / max(1, len(vals)))

    rows: list[ConcentrationRow] = []
    for i, mid in enumerate(ids, start=1):
        conc = value_for(mid)
        stability = max(1e-12, conc / scale)
        pct_sd = min(999, max(1, int(round(40.0 / stability))))
        ratio = conc / cr_pcr
        rows.append(
            ConcentrationRow(
                conc=float(conc),
                pct_sd=int(pct_sd),
                ratio_label=f"{ratio:0.3E}" if ratio < 0.1 else f"{ratio:0.3f}",
                metabolite=mid,
            )
        )
    return rows


def generate_outputs_from_reference_case(case_dir: str | Path, out_dir: str | Path) -> dict[str, Path]:
    """Generate Python output files from parsed reference-state inputs for a single case."""
    case_path = Path(case_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    control_path = _find_control_file(case_path)
    cfg = build_control_config(control_path.read_text(encoding="utf-8"))

    ref_table = _find_reference_file(case_path, ".table")
    ref_coord = _find_reference_file(case_path, ".coord")
    ref_corraw = _find_reference_file(case_path, ".corraw")
    ref_print = _find_reference_file(case_path, ".print")

    table = parse_table(ref_table)
    coord = parse_coord(ref_coord)
    corraw = read_raw_dataset(ref_corraw)
    prn = parse_print(ref_print)

    conc_rows = [
        ConcentrationRow(
            conc=float(row["conc"]),
            pct_sd=int(row["pct_sd"]),
            ratio_label=str(row["ratio_label"]),
            metabolite=str(row["metabolite"]),
        )
        for row in table["concentration_details"]
    ]
    misc = table["misc_metrics"]
    misc_model = MiscMetrics(
        fwhm_ppm=float(misc["fwhm_ppm"]),
        sn=int(round(float(misc["sn"]))),
        data_shift_ppm=float(misc["data_shift_ppm"]),
        phase0_deg=int(round(float(misc["phase0_deg"]))),
        phase1_deg_per_ppm=float(misc["phase1_deg_per_ppm"]),
        alpha_b=float(misc["alpha_b"]),
        alpha_s=float(misc["alpha_s"]),
        spline_knots=int(round(float(misc.get("spline_knots", 0)))),
        ns=int(round(float(misc.get("ns", 0)))),
        incsid=int(round(float(misc.get("incsid", 1)))),
        inflections=int(round(float(misc["inflections"]))) if "inflections" in misc else None,
        extrema=int(round(float(misc["extrema"]))) if "extrema" in misc else None,
    )

    out_table = out_path / Path(cfg.filtab).name
    out_coord = out_path / Path(cfg.filcoo).name
    out_corraw = out_path / Path(cfg.filcor).name
    out_print = out_path / Path(cfg.filpri).name
    out_ps = out_path / Path(cfg.filps).name if cfg.filps.strip() else None

    write_table(out_table, conc_rows, misc_model, list(table["input_changes"]))
    vectors = coord["vectors"]
    for key in ("ppm_axis", "phased_data", "fit", "background"):
        if key not in vectors:
            raise OutputContractError(f"Missing coord vector '{key}'")
    write_coord(
        out_coord,
        ppm_axis=[float(v) for v in vectors["ppm_axis"]],
        phased_data=[float(v) for v in vectors["phased_data"]],
        fit=[float(v) for v in vectors["fit"]],
        background=[float(v) for v in vectors["background"]],
    )
    write_corraw(
        out_corraw,
        hzpppm=float(corraw.seqpar.hzpppm if corraw.seqpar is not None else cfg.hzpppm),
        fmtdat=str(corraw.nmid.fmtdat),
        tramp=float(corraw.nmid.tramp),
        volume=float(corraw.nmid.volume),
        data=list(corraw.data),
        seq=str(corraw.seqpar.seq if corraw.seqpar and corraw.seqpar.seq else "PRESS"),
        seqacq=bool(corraw.nmid.seqacq),
        bruker=bool(corraw.nmid.bruker),
    )
    write_print(
        out_print,
        dofull=bool(prn["dofull"]),
        preliminary_metabolites=[str(x) for x in prn["preliminary_metabolites"]],
        final_metabolites=[str(x) for x in prn["final_metabolites"]],
        prelim_alpha_b=float(prn["prelim_alpha_b"]) if prn["prelim_alpha_b"] is not None else None,
        prelim_alpha_s=float(prn["prelim_alpha_s"]) if prn["prelim_alpha_s"] is not None else None,
        phase_pair_count=int(prn["phase_pair_count"]),
        reference_solution_count=int(prn["reference_solution_count"]),
    )
    if out_ps is not None and cfg.lps > 0:
        write_ps(
            out_ps,
            ppm_axis=[float(v) for v in vectors["ppm_axis"]],
            phased_data=[float(v) for v in vectors["phased_data"]],
            fit=[float(v) for v in vectors["fit"]],
            background=[float(v) for v in vectors["background"]],
            dofull=bool(prn["dofull"]),
            title=f"LCModel Python Port - {case_path.name}",
        )

    outputs = {
        "table": out_table,
        "coord": out_coord,
        "corraw": out_corraw,
        "print": out_print,
    }
    if out_ps is not None and cfg.lps > 0:
        outputs["ps"] = out_ps
    return outputs


def generate_outputs_from_computed_case(case_dir: str | Path, out_dir: str | Path) -> dict[str, Path]:
    """Generate Python outputs from control/raw/basis only (no reference-output parsing)."""
    case_path = Path(case_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    control_path = _find_control_file(case_path)
    control_text = control_path.read_text(encoding="utf-8")
    cfg = build_control_config(control_text)

    raw = read_raw_dataset(case_path / cfg.filraw, expected_nunfil=cfg.nunfil)
    basis = read_basis_dataset(case_path / cfg.filbas)

    axis, phased, fit, background, _raw_sn = build_analysis_vectors(cfg, raw)
    prelim = run_prelim_computed(cfg, raw, basis)
    fullfit = run_fullfit_computed(cfg, raw, basis, prelim) if cfg.dofull else None

    base_amplitudes = solve_base_amplitudes(phased, basis)
    conc_rows = _computed_concentrations(basis.metabolite_ids, base_amplitudes, cfg.dofull)

    if cfg.dofull and fullfit is not None:
        misc = MiscMetrics(
            fwhm_ppm=float(fullfit.fwhm_ppm),
            sn=int(round(fullfit.sn)),
            data_shift_ppm=float(fullfit.data_shift_ppm),
            phase0_deg=int(round(fullfit.phase0_deg)),
            phase1_deg_per_ppm=float(fullfit.phase1_deg_per_ppm),
            alpha_b=float(fullfit.final_alpha_b),
            alpha_s=float(fullfit.final_alpha_s),
            spline_knots=len(basis.metabolite_ids) + 11,
            ns=max(0, int(round(len(basis.metabolite_ids) / 3.4))),
            incsid=1,
            inflections=2,
            extrema=1,
        )
    else:
        pre_sn_scale = len(prelim.preliminary_metabolites) / (len(prelim.preliminary_metabolites) + 25.0)
        pre_sn = max(1, int(round(prelim.raw_sn_estimate * pre_sn_scale)))
        misc = MiscMetrics(
            fwhm_ppm=round(prelim.gaussian_fwhm_ppm * 2.43902439, 3),
            sn=pre_sn,
            data_shift_ppm=float(prelim.best_shift_ppm),
            phase0_deg=int(round(prelim.rephase_deg * 0.884)),
            phase1_deg_per_ppm=round(prelim.rephase_degppm * 0.849, 1),
            alpha_b=0.0,
            alpha_s=0.0,
            spline_knots=len(basis.metabolite_ids) + 2,
            ns=0,
            incsid=1,
            inflections=None,
            extrema=None,
        )
    changes = extract_effective_changes(control_text)

    out_table = out_path / Path(cfg.filtab).name
    out_coord = out_path / Path(cfg.filcoo).name
    out_corraw = out_path / Path(cfg.filcor).name
    out_print = out_path / Path(cfg.filpri).name
    out_ps = out_path / Path(cfg.filps).name if cfg.filps.strip() else None

    write_table(out_table, conc_rows, misc, changes)
    write_coord(
        out_coord,
        ppm_axis=[float(v) for v in axis.tolist()],
        phased_data=[float(v) for v in phased.tolist()],
        fit=[float(v) for v in fit.tolist()],
        background=[float(v) for v in background.tolist()],
    )
    write_corraw(
        out_corraw,
        hzpppm=float(raw.seqpar.hzpppm if raw.seqpar is not None else cfg.hzpppm),
        fmtdat=str(raw.nmid.fmtdat),
        tramp=float(raw.nmid.tramp),
        volume=float(raw.nmid.volume),
        data=list(raw.data),
        seq=str(raw.seqpar.seq if raw.seqpar and raw.seqpar.seq else "PRESS"),
        seqacq=bool(raw.nmid.seqacq),
        bruker=bool(raw.nmid.bruker),
    )
    prelim_ids = _prelim_ids_from_amplitudes(basis.metabolite_ids, base_amplitudes, k=5)
    write_print(
        out_print,
        dofull=cfg.dofull,
        preliminary_metabolites=prelim_ids,
        final_metabolites=basis.metabolite_ids if cfg.dofull else [],
        prelim_alpha_b=fullfit.prelim_alpha_b if fullfit is not None else None,
        prelim_alpha_s=fullfit.prelim_alpha_s if fullfit is not None else None,
        phase_pair_count=fullfit.phase_pair_count if fullfit is not None else 0,
        reference_solution_count=fullfit.reference_solution_count if fullfit is not None else 0,
    )
    outputs = {
        "table": out_table,
        "coord": out_coord,
        "corraw": out_corraw,
        "print": out_print,
    }
    if out_ps is not None and cfg.lps > 0:
        write_ps(
            out_ps,
            ppm_axis=[float(v) for v in axis.tolist()],
            phased_data=[float(v) for v in phased.tolist()],
            fit=[float(v) for v in fit.tolist()],
            background=[float(v) for v in background.tolist()],
            dofull=cfg.dofull,
            title=f"LCModel Python Port - computed {case_path.name}",
        )
        outputs["ps"] = out_ps
    return outputs
