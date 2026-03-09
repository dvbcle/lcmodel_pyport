"""Writer for LCModel-like .coord output contracts."""

from __future__ import annotations

from pathlib import Path


def _chunks(values: list[float], width: int = 10) -> list[str]:
    out: list[str] = []
    for i in range(0, len(values), width):
        out.append(" " + "".join(f"{v:13.6f}" for v in values[i : i + width]))
    return out


def render_coord(ppm_axis: list[float], phased_data: list[float], fit: list[float], background: list[float]) -> str:
    ny = len(ppm_axis)
    if not (len(phased_data) == ny and len(fit) == ny and len(background) == ny):
        raise ValueError("coord vectors must have matching length")

    lines: list[str] = []
    lines.append(f" {ny:4d} points on ppm-axis = NY")
    lines.extend(_chunks(ppm_axis))
    lines.append(" NY phased data points follow")
    lines.extend(_chunks(phased_data))
    lines.append(" NY points of the fit to the data follow")
    lines.extend(_chunks(fit))
    lines.append(" NY background values follow")
    lines.extend(_chunks(background))
    lines.append("")
    return "\n".join(lines)


def write_coord(path: str | Path, ppm_axis: list[float], phased_data: list[float], fit: list[float], background: list[float]) -> None:
    Path(path).write_text(render_coord(ppm_axis, phased_data, fit, background), encoding="utf-8")
