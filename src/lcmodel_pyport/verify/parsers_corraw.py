"""Parser facade for corrected RAW files."""

from __future__ import annotations

from pathlib import Path

from lcmodel_pyport.io.raw_reader import read_raw_dataset


def parse_corraw(path: str | Path) -> dict[str, object]:
    ds = read_raw_dataset(path)
    return {
        "has_seqpar": ds.seqpar is not None,
        "has_nmid": ds.nmid.fmtdat.strip() != "",
        "n_points": len(ds.data),
    }

