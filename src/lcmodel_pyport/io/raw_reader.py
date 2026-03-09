"""RAW/CORAW reader utilities for gate G1 tests."""

from __future__ import annotations

import re
from pathlib import Path

from lcmodel_pyport.config.models import NmidMetadata, RawDataset, SeqParMetadata
from lcmodel_pyport.core.errors import InputFormatError, ValidationError
from lcmodel_pyport.io.namelist_utils import find_block, parse_block_values
from lcmodel_pyport.validation.schemas import validate_raw_dataset

_PAIR_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s+([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s*$"
)


def compute_raw_scale(fcalib: float, tramp: float, volume: float) -> float:
    for name, value in (("fcalib", fcalib), ("tramp", tramp), ("volume", volume)):
        if value <= 0:
            raise ValidationError(f"{name} must be > 0")
    return fcalib * tramp / volume


def _parse_complex_pairs(lines: list[str], start_line: int) -> list[complex]:
    out: list[complex] = []
    for i in range(start_line, len(lines)):
        m = _PAIR_RE.match(lines[i].strip())
        if not m:
            continue
        out.append(complex(float(m.group(1)), float(m.group(2))))
    if not out:
        raise InputFormatError("No complex samples found after NMID block")
    return out


def read_raw_dataset(path: str | Path, expected_nunfil: int | None = None) -> RawDataset:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()

    nmid_block = find_block(lines, "NMID")
    if nmid_block is None:
        raise InputFormatError("NMID block not found")
    nmid_values = parse_block_values(lines, *nmid_block)
    if "fmtdat" not in nmid_values:
        raise InputFormatError("NMID.FMTDAT is required")

    nmid = NmidMetadata(
        id=str(nmid_values.get("id", "")),
        fmtdat=str(nmid_values["fmtdat"]),
        tramp=float(nmid_values.get("tramp", 1.0)),
        volume=float(nmid_values.get("volume", 1.0)),
        seqacq=bool(nmid_values.get("seqacq", False)),
        bruker=bool(nmid_values.get("bruker", False)),
    )

    seqpar = None
    seqpar_block = find_block(lines, "SEQPAR")
    if seqpar_block is not None:
        seq_values = parse_block_values(lines, *seqpar_block)
        if "hzpppm" in seq_values:
            seqpar = SeqParMetadata(
                hzpppm=float(seq_values["hzpppm"]),
                echot=float(seq_values["echot"]) if "echot" in seq_values else None,
                seq=str(seq_values["seq"]) if "seq" in seq_values else None,
            )

    data = _parse_complex_pairs(lines, nmid_block[1] + 1)
    dataset = RawDataset(seqpar=seqpar, nmid=nmid, data=data)
    validate_raw_dataset(dataset, expected_nunfil=expected_nunfil)
    return dataset

