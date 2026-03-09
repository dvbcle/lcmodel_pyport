"""Typed models for early porting stages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ControlConfig:
    key: Optional[int]
    nunfil: int
    deltat: float
    hzpppm: float
    filbas: str
    filraw: str
    filps: str
    dofull: bool
    filpri: Optional[str] = None
    filcoo: Optional[str] = None
    filtab: Optional[str] = None
    filcor: Optional[str] = None
    lprint: int = 0
    lcoord: int = 0
    ltable: int = 0
    lcoraw: int = 0
    lps: int = 8


@dataclass(frozen=True)
class SeqParMetadata:
    hzpppm: float
    echot: Optional[float] = None
    seq: Optional[str] = None


@dataclass(frozen=True)
class NmidMetadata:
    id: str
    fmtdat: str
    tramp: float
    volume: float
    seqacq: bool
    bruker: bool


@dataclass(frozen=True)
class RawDataset:
    seqpar: Optional[SeqParMetadata]
    nmid: NmidMetadata
    data: list[complex]

