"""Minimal namelist parsing helpers for NMID/SEQPAR."""

from __future__ import annotations

import re

_HEADER_RE = re.compile(r"^\s*([$&])([A-Za-z0-9_]+)")
_KV_RE = re.compile(r"([A-Za-z0-9_]+)\s*=\s*([^,]+)")


def parse_scalar(raw: str) -> object:
    value = raw.strip()
    end_pos = value.upper().find("$END")
    if end_pos >= 0:
        value = value[:end_pos].strip()
    value = value.rstrip(",")
    lower = value.lower()
    if lower in {"t", ".true.", "true"}:
        return True
    if lower in {"f", ".false.", "false"}:
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


def find_block(lines: list[str], name: str) -> tuple[int, int] | None:
    upper_name = name.upper()
    start = -1
    for i, line in enumerate(lines):
        m = _HEADER_RE.match(line)
        if not m:
            continue
        if m.group(2).upper() == upper_name:
            start = i
            break
    if start < 0:
        return None
    if "$END" in lines[start].upper():
        return (start, start)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        upper = stripped.upper()
        if upper.startswith("$END") or "$END" in upper or stripped == "/":
            return (start, j)
    return (start, len(lines) - 1)


def parse_block_values(lines: list[str], start: int, end: int) -> dict[str, object]:
    values: dict[str, object] = {}
    for i in range(start, end + 1):
        line = lines[i]
        for m in _KV_RE.finditer(line):
            key = m.group(1).strip().lower()
            values[key] = parse_scalar(m.group(2).strip())
    return values
