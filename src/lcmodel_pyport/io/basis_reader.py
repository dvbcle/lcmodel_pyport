"""Basis file reader helpers for stage-level checkpoint tests."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from lcmodel_pyport.io.namelist_utils import parse_block_values

_HEADER_RE = re.compile(r"^\s*([$&])([A-Za-z0-9_]+)")
_FLOAT_RE = re.compile(r"[+-]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[Ee][+-]?\d+)?")


@dataclass(frozen=True)
class BasisEntry:
    id: str
    metabolo: str
    conc: float
    tramp: float
    volume: float
    ishift: int
    data: list[complex]


@dataclass(frozen=True)
class BasisDataset:
    idbasi: str
    fmtdat: str
    badelt: float
    ndatab: int
    metabolite_ids: list[str]
    entries: list[BasisEntry]


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

    ndatab_raw = basis1.get("ndatab", 0)
    if isinstance(ndatab_raw, str):
        ndatab_raw = ndatab_raw.split()[0]
    ndatab = int(ndatab_raw)

    basis_blocks = _find_blocks(lines, "BASIS")
    ids: list[str] = []
    entries: list[BasisEntry] = []
    for bi, block in enumerate(basis_blocks):
        values = parse_block_values(lines, *block)
        if "id" not in values:
            continue
        metab_id = str(values["id"])
        ids.append(metab_id)
        next_start = basis_blocks[bi + 1][0] if (bi + 1) < len(basis_blocks) else len(lines)
        floats: list[float] = []
        for i in range(block[1] + 1, next_start):
            if _HEADER_RE.match(lines[i]):
                break
            floats.extend(float(tok) for tok in _FLOAT_RE.findall(lines[i]))
            if len(floats) >= (2 * ndatab):
                break
        if len(floats) >= 2:
            pair_count = min(ndatab, len(floats) // 2)
            data = [complex(floats[2 * k], floats[(2 * k) + 1]) for k in range(pair_count)]
        else:
            data = [0j] * ndatab
        if len(data) < ndatab:
            data.extend([0j] * (ndatab - len(data)))
        entries.append(
            BasisEntry(
                id=metab_id,
                metabolo=str(values.get("metabo", metab_id)),
                conc=float(values.get("conc", 1.0)),
                tramp=float(values.get("tramp", 1.0)),
                volume=float(values.get("volume", 1.0)),
                ishift=int(values.get("ishift", 0)),
                data=data,
            )
        )

    return BasisDataset(
        idbasi=str(basis1.get("idbasi", "")),
        fmtdat=str(basis1.get("fmtbas", "")),
        badelt=float(basis1.get("badelt", 0.0)),
        ndatab=ndatab,
        metabolite_ids=ids,
        entries=entries,
    )
