"""PS-input checkpoint extraction helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from lcmodel_pyport.verify.parsers_coord import parse_coord
from lcmodel_pyport.verify.parsers_print import parse_print
from lcmodel_pyport.verify.parsers_ps import parse_ps


@dataclass(frozen=True)
class PsInputCheckpoint:
    ny: int
    dofull: bool
    has_crude_model_marker: bool
    ppm_first: float
    ppm_last: float
    phased_head3: list[float]
    fit_head3: list[float]
    background_head3: list[float]
    phased_min: float
    phased_max: float
    fit_min: float
    fit_max: float
    background_min: float
    background_max: float


def build_ps_input_checkpoint(coord_path: str | Path, print_path: str | Path, ps_path: str | Path) -> PsInputCheckpoint:
    coord = parse_coord(coord_path)
    prn = parse_print(print_path)
    ps = parse_ps(ps_path)
    vectors = coord["vectors"]
    return PsInputCheckpoint(
        ny=int(coord["ny"]),
        dofull=bool(prn["dofull"]),
        has_crude_model_marker=bool(ps["has_crude_model_marker"]),
        ppm_first=float(vectors["ppm_axis"][0]),
        ppm_last=float(vectors["ppm_axis"][-1]),
        phased_head3=[float(x) for x in vectors["phased_data"][:3]],
        fit_head3=[float(x) for x in vectors["fit"][:3]],
        background_head3=[float(x) for x in vectors["background"][:3]],
        phased_min=float(min(vectors["phased_data"])),
        phased_max=float(max(vectors["phased_data"])),
        fit_min=float(min(vectors["fit"])),
        fit_max=float(max(vectors["fit"])),
        background_min=float(min(vectors["background"])),
        background_max=float(max(vectors["background"])),
    )


def checkpoint_to_dict(cp: PsInputCheckpoint) -> dict[str, object]:
    return asdict(cp)
