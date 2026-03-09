"""Writer for visual-inspection PostScript output."""

from __future__ import annotations

from pathlib import Path


def _normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    vmin = min(values)
    vmax = max(values)
    if vmax - vmin <= 0:
        return [0.0 for _ in values]
    return [(v - vmin) / (vmax - vmin) for v in values]


def _polyline(values: list[float], x0: float, y0: float, w: float, h: float) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    n = len(values)
    norm = _normalize(values)
    for i, y in enumerate(norm):
        x = x0 + (w * i / max(1, n - 1))
        yy = y0 + h * y
        cmd = "moveto" if i == 0 else "lineto"
        out.append(f"{x:.2f} {yy:.2f} {cmd}")
    return out


def render_ps(
    ppm_axis: list[float],
    phased_data: list[float],
    fit: list[float],
    background: list[float],
    dofull: bool,
    title: str = "LCModel Python Port - Visual Parity Preview",
) -> str:
    lines: list[str] = []
    lines.append("%!PS-Adobe-3.0")
    lines.append("%%BoundingBox: 0 0 612 792")
    lines.append("/Helvetica findfont 10 scalefont setfont")
    lines.append(f"50 770 moveto ({title}) show")
    lines.append(f"50 755 moveto (DOFULL={'T' if dofull else 'F'}) show")
    if not dofull:
        lines.append("/Helvetica-Bold findfont 12 scalefont setfont")
        lines.append("50 738 moveto (CRUDE MODEL) show")
        lines.append("/Helvetica findfont 10 scalefont setfont")

    # Plot area
    x0, y0, w, h = 50.0, 120.0, 520.0, 560.0
    lines.append("newpath")
    lines.append(f"{x0:.2f} {y0:.2f} moveto")
    lines.append(f"{x0+w:.2f} {y0:.2f} lineto")
    lines.append(f"{x0+w:.2f} {y0+h:.2f} lineto")
    lines.append(f"{x0:.2f} {y0+h:.2f} lineto")
    lines.append("closepath stroke")

    for color, vec, label_y in (
        ("0 0 0", phased_data, 105),
        ("0 0.4 0.9", fit, 92),
        ("0.8 0.2 0.2", background, 79),
    ):
        lines.append(f"{color} setrgbcolor")
        lines.append("newpath")
        lines.extend(_polyline(vec, x0, y0, w, h))
        lines.append("stroke")
        lines.append("0 0 0 setrgbcolor")
        lines.append(f"50 {label_y} moveto (trace color {color}) show")

    if ppm_axis:
        lines.append(f"50 60 moveto (ppm range: {ppm_axis[0]:.3f} .. {ppm_axis[-1]:.3f}) show")
    lines.append("showpage")
    lines.append("")
    return "\n".join(lines)


def write_ps(
    path: str | Path,
    ppm_axis: list[float],
    phased_data: list[float],
    fit: list[float],
    background: list[float],
    dofull: bool,
    title: str = "LCModel Python Port - Visual Parity Preview",
) -> None:
    Path(path).write_text(
        render_ps(
            ppm_axis=ppm_axis,
            phased_data=phased_data,
            fit=fit,
            background=background,
            dofull=dofull,
            title=title,
        ),
        encoding="utf-8",
    )
