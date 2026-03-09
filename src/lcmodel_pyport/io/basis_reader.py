"""Basis file reader helpers for stage-level checkpoint tests."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from lcmodel_pyport.io.namelist_utils import parse_block_values

_HEADER_RE = re.compile(r"^\s*([$&])([A-Za-z0-9_]+)")


@dataclass(frozen=True)
class BasisDataset:
    idbasi: str
    fmtdat: str
    badelt: float
    ndatab: int
    metabolite_ids: list[str]


def _find_blocks(lines: list[str], name: str) -> list[tuple[int, int]]:
    upper = name.upper()
    blocks: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        m = _HEADER_RE.match(lines[i])
        if not m or m.group(2).upper() != upper:
            i += 1
            continue
        start = i
        if "$END" in lines[start].upper():
            blocks.append((start, start))
            i = start + 1
            continue
        end = len(lines) - 1
        j = i + 1
        while j < len(lines):
            stripped = lines[j].strip()
            upper_line = stripped.upper()
            if upper_line.startswith("$END") or "$END" in upper_line or stripped == "/":
                end = j
                break
            j += 1
        blocks.append((start, end))
        i = end + 1
    return blocks


def read_basis_dataset(path: str | Path) -> BasisDataset:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    basis1_blocks = _find_blocks(lines, "BASIS1")
    if not basis1_blocks:
        raise ValueError("BASIS1 block not found")
    basis1 = parse_block_values(lines, *basis1_blocks[0])

    ids: list[str] = []
    for block in _find_blocks(lines, "BASIS"):
        values = parse_block_values(lines, *block)
        if "id" in values:
            ids.append(str(values["id"]))

    ndatab_raw = basis1.get("ndatab", 0)
    if isinstance(ndatab_raw, str):
        ndatab_raw = ndatab_raw.split()[0]

    return BasisDataset(
        idbasi=str(basis1.get("idbasi", "")),
        fmtdat=str(basis1.get("fmtbas", "")),
        badelt=float(basis1.get("badelt", 0.0)),
        ndatab=int(ndatab_raw),
        metabolite_ids=ids,
    )
