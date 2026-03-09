"""Writer for LCModel-like .table output contracts."""

from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.report.models import ConcentrationRow, MiscMetrics


def render_table(
    conc_rows: list[ConcentrationRow],
    misc: MiscMetrics,
    input_changes: list[str],
    version: str = "LCModel (Version 6.3-1N)",
) -> str:
    lines: list[str] = [f" {version}", "  ", ""]
    lines.append(f"$$CONC {len(conc_rows) + 1:2d} lines in following concentration table = NCONC+1")
    lines.append("    Conc.  %SD /Cr+PCr  Metabolite                                         ")
    for row in conc_rows:
        lines.append(f" {row.conc:8.2E} {row.pct_sd:3d}% {row.ratio_label:>7} {row.metabolite:<12}")
    lines.append("")

    misc_lines = [
        f"  FWHM = {misc.fwhm_ppm:0.3f} ppm    S/N = {misc.sn:3d}",
        f"  Data shift = {misc.data_shift_ppm:0.3f} ppm",
        f"  Ph: {misc.phase0_deg:3d} deg {misc.phase1_deg_per_ppm:9.1f} deg/ppm",
        f"  alphaB,S = {misc.alpha_b:0.1E}, {misc.alpha_s:9.1E}",
        f"   {misc.spline_knots:2d} spline knots.   Ns = {misc.ns}({misc.incsid})",
    ]
    if misc.inflections is not None and misc.extrema is not None:
        misc_lines.append(f"   {misc.inflections:1d} inflections.     {misc.extrema:1d} extrema")

    lines.append(f"$$MISC {len(misc_lines):2d} lines in following misc. output table")
    lines.extend(misc_lines)
    lines.append("")
    lines.append("$$DIAG  0 lines in following diagnostic table:")
    lines.append("")
    lines.append(f"$$INPU {len(input_changes):2d} lines in following table of input changes:")
    lines.extend(input_changes)
    lines.append("")
    return "\n".join(lines)


def write_table(
    path: str | Path,
    conc_rows: list[ConcentrationRow],
    misc: MiscMetrics,
    input_changes: list[str],
) -> None:
    Path(path).write_text(render_table(conc_rows, misc, input_changes), encoding="utf-8")
