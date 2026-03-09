"""Writer for simplified LCModel-like .print diagnostics markers."""

from __future__ import annotations

from pathlib import Path


def render_print(
    dofull: bool,
    preliminary_metabolites: list[str],
    final_metabolites: list[str] | None = None,
    prelim_alpha_b: float | None = None,
    prelim_alpha_s: float | None = None,
    phase_pair_count: int = 0,
    reference_solution_count: int = 0,
) -> str:
    lines: list[str] = []
    lines.append(" LCModel (Python port diagnostic print)")
    lines.append(f" DOFULL={'T' if dofull else 'F'},")
    lines.append("")
    lines.append("                    Basis Spectra used for the Preliminary Analysis")
    for i, metab in enumerate(preliminary_metabolites, start=1):
        lines.append(f" {i:3d}       {metab:<8}")
    lines.append("")

    if dofull and final_metabolites:
        lines.append("                    Basis Spectra used for the Final Analysis")
        for i, metab in enumerate(final_metabolites, start=1):
            lines.append(f" {i:3d}       {metab:<8}")
        lines.append("")
        if prelim_alpha_b is not None and prelim_alpha_s is not None:
            lines.append(
                f"                    Preliminary full analysis with alphaB = {prelim_alpha_b:0.2E} and alphaS = {prelim_alpha_s:0.2E}"
            )
            lines.append("")
        for _ in range(reference_solution_count):
            lines.append("                    Reference Solution for rephased data")
            lines.append("")
        for i in range(phase_pair_count):
            lines.append(f"          Phase Pair {i+1:1d}     Decrease 1 of alphaB/alphaS")
    lines.append("")
    return "\n".join(lines)


def write_print(
    path: str | Path,
    dofull: bool,
    preliminary_metabolites: list[str],
    final_metabolites: list[str] | None = None,
    prelim_alpha_b: float | None = None,
    prelim_alpha_s: float | None = None,
    phase_pair_count: int = 0,
    reference_solution_count: int = 0,
) -> None:
    Path(path).write_text(
        render_print(
            dofull=dofull,
            preliminary_metabolites=preliminary_metabolites,
            final_metabolites=final_metabolites,
            prelim_alpha_b=prelim_alpha_b,
            prelim_alpha_s=prelim_alpha_s,
            phase_pair_count=phase_pair_count,
            reference_solution_count=reference_solution_count,
        ),
        encoding="utf-8",
    )
