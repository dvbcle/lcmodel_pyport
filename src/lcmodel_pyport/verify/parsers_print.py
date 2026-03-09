"""Parser for LCModel detailed .print output."""

from __future__ import annotations

import re
from pathlib import Path


_FULL_MARKERS = (
    "Preliminary full analysis with alphaB",
    "Phase Pair",
    "Reference Solution for rephased data",
)
_METAB_LINE_RE = re.compile(r"^\s*\d+\s+([A-Za-z+\-][A-Za-z0-9+\-]*)\b")
_BEST_SHIFT_RE = re.compile(
    r"Best data shift for all starting shifts so far =\s*([+-]?\d+)\s+points\s*=\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s*ppm"
)
_REPHASE_RE = re.compile(
    r"Rephasing to\s*([+-]?\d+(?:\.\d+)?)\s*deg;\s*([+-]?\d+(?:\.\d+)?)\s*deg/ppm"
)
_FWHM_RE = re.compile(r"Gaussian FWHM \(ppm\)\s*=\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)")


def _collect_metabolites(lines: list[str], header: str, stop_tokens: tuple[str, ...]) -> list[str]:
    start = next((i for i, line in enumerate(lines) if header in line), None)
    if start is None:
        return []
    out: list[str] = []
    for i in range(start + 1, len(lines)):
        line = lines[i]
        if any(token in line for token in stop_tokens):
            break
        m = _METAB_LINE_RE.match(line)
        if m:
            out.append(m.group(1))
    return out


def parse_print(path: str | Path) -> dict[str, object]:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    dofull = None
    for line in lines:
        if "DOFULL=" in line:
            if "DOFULL=T" in line.upper():
                dofull = True
            elif "DOFULL=F" in line.upper():
                dofull = False
            break
    found_markers = [m for m in _FULL_MARKERS if any(m in line for line in lines)]
    prelim_metabs = _collect_metabolites(
        lines,
        "Basis Spectra used for the Preliminary Analysis",
        (
            "Peak in CCF at",
            "Starting values for final analysis",
            "Preliminary full analysis with alphaB",
        ),
    )
    final_metabs = _collect_metabolites(
        lines,
        "Basis Spectra used for the Final Analysis",
        ("Preliminary full analysis with alphaB",),
    )

    starting_shift_count = sum(1 for line in lines if "Starting shift =" in line)
    best_shift_points = None
    best_shift_ppm = None
    for line in lines:
        m = _BEST_SHIFT_RE.search(line)
        if m:
            best_shift_points = int(m.group(1))
            best_shift_ppm = float(m.group(2))

    rephase_deg = None
    rephase_degppm = None
    for line in lines:
        m = _REPHASE_RE.search(line)
        if m:
            rephase_deg = float(m.group(1))
            rephase_degppm = float(m.group(2))

    gaussian_fwhm_ppm = None
    for line in lines:
        m = _FWHM_RE.search(line)
        if m:
            gaussian_fwhm_ppm = float(m.group(1))

    return {
        "dofull": dofull,
        "markers": found_markers,
        "preliminary_metabolites": prelim_metabs,
        "final_metabolites": final_metabs,
        "starting_shift_count": starting_shift_count,
        "best_shift_points": best_shift_points,
        "best_shift_ppm": best_shift_ppm,
        "rephase_deg": rephase_deg,
        "rephase_degppm": rephase_degppm,
        "gaussian_fwhm_ppm": gaussian_fwhm_ppm,
        "has_optimal_shift_section": any("Analysis with optimal data shift" in line for line in lines),
    }
