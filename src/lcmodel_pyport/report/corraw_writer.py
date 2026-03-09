"""Writer for corrected RAW output contract."""

from __future__ import annotations

from pathlib import Path


def render_corraw(
    hzpppm: float,
    fmtdat: str,
    tramp: float,
    volume: float,
    data: list[complex],
    seq: str = "PRESS",
    seqacq: bool = False,
    bruker: bool = False,
) -> str:
    lines: list[str] = []
    lines.append(" $SEQPAR")
    lines.append(f" HZPPPM =  {hzpppm:.6f},")
    lines.append(f" SEQ = '{seq}' $END")
    lines.append(" $NMID")
    lines.append(f" FMTDAT = '{fmtdat}',")
    lines.append(f" TRAMP =  {tramp:.6f},")
    lines.append(f" VOLUME =  {volume:.6f},")
    lines.append(f" SEQACQ = {'T' if seqacq else 'F'},")
    lines.append(f" BRUKER = {'T' if bruker else 'F'} $END")
    for z in data:
        lines.append(f" {z.real:13.6E} {z.imag:13.6E}")
    lines.append("")
    return "\n".join(lines)


def write_corraw(
    path: str | Path,
    hzpppm: float,
    fmtdat: str,
    tramp: float,
    volume: float,
    data: list[complex],
    seq: str = "PRESS",
    seqacq: bool = False,
    bruker: bool = False,
) -> None:
    Path(path).write_text(
        render_corraw(
            hzpppm=hzpppm,
            fmtdat=fmtdat,
            tramp=tramp,
            volume=volume,
            data=data,
            seq=seq,
            seqacq=seqacq,
            bruker=bruker,
        ),
        encoding="utf-8",
    )
