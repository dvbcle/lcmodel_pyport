"""Parser for LCModel .table files."""

from __future__ import annotations

import re
from pathlib import Path

_CONC_ROW_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s+(\d+)%\s+(\S+)\s+(\S+)\s*$"
)
_FWHM_SN_RE = re.compile(
    r"FWHM\s*=\s*([+-]?\d+(?:\.\d+)?)\s*ppm\s+S/N\s*=\s*([+-]?\d+)"
)
_SHIFT_RE = re.compile(r"Data shift\s*=\s*([+-]?\d+(?:\.\d+)?)\s*ppm")
_PHASE_RE = re.compile(r"Ph:\s*([+-]?\d+)\s*deg\s*([+-]?\d+(?:\.\d+)?)\s*deg/ppm")
_ALPHA_RE = re.compile(
    r"alphaB,S\s*=\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?),\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)"
)
_SPLINE_RE = re.compile(r"(\d+)\s+spline knots\.\s+Ns\s*=\s*(\d+)\((\d+)\)")
_INFLEX_RE = re.compile(r"(\d+)\s+inflections\.\s+(\d+)\s+extrema")


def parse_table(path: str | Path) -> dict[str, object]:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    sections: list[str] = []
    by_section: dict[str, list[str]] = {}
    current = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("$$"):
            current = stripped.split()[0]
            sections.append(current)
            by_section[current] = []
            continue
        if current:
            by_section[current].append(line.rstrip())
    conc_rows: list[dict[str, object]] = []
    for line in by_section.get("$$CONC", []):
        m = _CONC_ROW_RE.match(line)
        if not m:
            continue
        conc_rows.append(
            {
                "metabolite": m.group(4),
                "conc": float(m.group(1)),
                "pct_sd": int(m.group(2)),
                "ratio_label": m.group(3),
            }
        )

    misc_metrics: dict[str, float] = {}
    for raw in by_section.get("$$MISC", []):
        line = raw.strip()
        m = _FWHM_SN_RE.search(line)
        if m:
            misc_metrics["fwhm_ppm"] = float(m.group(1))
            misc_metrics["sn"] = float(m.group(2))
            continue
        m = _SHIFT_RE.search(line)
        if m:
            misc_metrics["data_shift_ppm"] = float(m.group(1))
            continue
        m = _PHASE_RE.search(line)
        if m:
            misc_metrics["phase0_deg"] = float(m.group(1))
            misc_metrics["phase1_deg_per_ppm"] = float(m.group(2))
            continue
        m = _ALPHA_RE.search(line)
        if m:
            misc_metrics["alpha_b"] = float(m.group(1))
            misc_metrics["alpha_s"] = float(m.group(2))
            continue
        m = _SPLINE_RE.search(line)
        if m:
            misc_metrics["spline_knots"] = float(m.group(1))
            misc_metrics["ns"] = float(m.group(2))
            misc_metrics["incsid"] = float(m.group(3))
            continue
        m = _INFLEX_RE.search(line)
        if m:
            misc_metrics["inflections"] = float(m.group(1))
            misc_metrics["extrema"] = float(m.group(2))

    input_changes = [line.strip() for line in by_section.get("$$INPU", []) if line.strip()]

    return {
        "sections_order": sections,
        "sections": by_section,
        "concentration_rows": len(conc_rows),
        "concentration_details": conc_rows,
        "concentration_metabolites": [row["metabolite"] for row in conc_rows],
        "misc_metrics": misc_metrics,
        "input_changes": input_changes,
    }
