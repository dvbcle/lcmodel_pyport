"""Minimal output-stage generation using canonical parsed state."""

from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.config.control_parser import build_control_config
from lcmodel_pyport.core.errors import OutputContractError
from lcmodel_pyport.io.raw_reader import read_raw_dataset
from lcmodel_pyport.report.coord_writer import write_coord
from lcmodel_pyport.report.corraw_writer import write_corraw
from lcmodel_pyport.report.models import ConcentrationRow, MiscMetrics
from lcmodel_pyport.report.print_writer import write_print
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

    return {
        "table": out_table,
        "coord": out_coord,
        "corraw": out_corraw,
        "print": out_print,
    }
