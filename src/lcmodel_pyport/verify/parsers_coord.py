"""Parser for LCModel .coord files."""

from __future__ import annotations

from pathlib import Path


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
    return {"positions": positions}

