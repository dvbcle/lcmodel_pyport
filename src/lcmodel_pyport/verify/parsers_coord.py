"""Parser for LCModel .coord files."""

from __future__ import annotations

import re
from pathlib import Path

_FLOAT_RE = re.compile(r"[+-]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[Ee][+-]?\d+)?")


def _parse_float_block(lines: list[str], start_idx: int, n: int) -> list[float]:
    out: list[float] = []
    i = start_idx
    while i < len(lines) and len(out) < n:
        line = lines[i]
        if "follow" in line and i != start_idx:
            break
        out.extend(float(tok) for tok in _FLOAT_RE.findall(line))
        i += 1
    return out[:n]


def parse_coord(path: str | Path) -> dict[str, object]:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    markers = {
        "ppm_axis": "points on ppm-axis = NY",
        "phased_data": "NY phased data points follow",
        "fit": "NY points of the fit to the data follow",
        "background": "NY background values follow",
    }
    positions: dict[str, int] = {}
    for idx, line in enumerate(lines):
        for key, marker in markers.items():
            if marker in line:
                positions[key] = idx
    ny = None
    if "ppm_axis" in positions:
        tokens = _FLOAT_RE.findall(lines[positions["ppm_axis"]].split("points on ppm-axis = NY")[0])
        if tokens:
            ny = int(float(tokens[0]))

    vectors: dict[str, list[float]] = {}
    if ny is not None:
        if "ppm_axis" in positions:
            vectors["ppm_axis"] = _parse_float_block(lines, positions["ppm_axis"] + 1, ny)
        if "phased_data" in positions:
            vectors["phased_data"] = _parse_float_block(lines, positions["phased_data"] + 1, ny)
        if "fit" in positions:
            vectors["fit"] = _parse_float_block(lines, positions["fit"] + 1, ny)
        if "background" in positions:
            vectors["background"] = _parse_float_block(lines, positions["background"] + 1, ny)
    return {"positions": positions, "ny": ny, "vectors": vectors}
