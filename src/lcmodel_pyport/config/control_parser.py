"""LCMODL control parser for gate G1 tests."""

from __future__ import annotations

import re
from dataclasses import dataclass

from lcmodel_pyport.config.defaults import CONTROL_DEFAULTS
from lcmodel_pyport.config.models import ControlConfig
from lcmodel_pyport.core.errors import ControlParseError
from lcmodel_pyport.validation.schemas import validate_control_config

_ASSIGN_RE = re.compile(r"^\s*([^=]+?)\s*=\s*(.+?)\s*$")


@dataclass(frozen=True)
class Assignment:
    key: str
    value: object
    raw_value: str


def _parse_scalar(raw: str) -> object:
    value = raw.strip().rstrip(",")
    lower = value.lower()
    if lower in {".true.", "t", "true"}:
        return True
    if lower in {".false.", "f", "false"}:
        return False
    if (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    ):
        return value[1:-1]
    try:
        if any(ch in value.lower() for ch in (".", "e")):
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_assignments(text: str) -> list[Assignment]:
    lines = text.splitlines()
    in_block = False
    assignments: list[Assignment] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.upper().startswith("$LCMODL"):
            in_block = True
            continue
        if stripped.upper().startswith("$END"):
            break
        if not in_block:
            continue
        m = _ASSIGN_RE.match(stripped)
        if not m:
            continue
        key = m.group(1).strip().lower()
        raw_value = m.group(2).strip()
        parsed = _parse_scalar(raw_value)
        assignments.append(Assignment(key=key, value=parsed, raw_value=raw_value))
    if not assignments:
        raise ControlParseError("No LCMODL assignments found")
    return assignments


def parse_control_map(text: str) -> dict[str, object]:
    result = dict(CONTROL_DEFAULTS)
    for assignment in parse_assignments(text):
        result[assignment.key] = assignment.value
    return result


def build_control_config(text: str) -> ControlConfig:
    parsed = parse_control_map(text)
    try:
        cfg = ControlConfig(
            key=int(parsed["key"]) if "key" in parsed else None,
            nunfil=int(parsed["nunfil"]),
            deltat=float(parsed["deltat"]),
            hzpppm=float(parsed["hzpppm"]),
            filbas=str(parsed["filbas"]),
            filraw=str(parsed["filraw"]),
            filps=str(parsed["filps"]),
            dofull=bool(parsed.get("dofull", True)),
            filpri=str(parsed["filpri"]) if "filpri" in parsed else None,
            filcoo=str(parsed["filcoo"]) if "filcoo" in parsed else None,
            filtab=str(parsed["filtab"]) if "filtab" in parsed else None,
            filcor=str(parsed["filcor"]) if "filcor" in parsed else None,
            lprint=int(parsed.get("lprint", 0)),
            lcoord=int(parsed.get("lcoord", 0)),
            ltable=int(parsed.get("ltable", 0)),
            lcoraw=int(parsed.get("lcoraw", 0)),
            lps=int(parsed.get("lps", 8)),
        )
    except KeyError as exc:
        raise ControlParseError(f"Missing required control field: {exc.args[0]}") from exc
    validate_control_config(cfg)
    return cfg

