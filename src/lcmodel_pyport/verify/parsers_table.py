"""Parser for LCModel .table files."""

from __future__ import annotations

import re
from pathlib import Path

_CONC_ROW_RE = re.compile(
    r"^\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s+\d+%\s+[^\s]+\s+(\S+)\s*$"
)


def parse_table(path: str | Path) -> dict[str, object]:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    sections: list[str] = []
    by_section: dict[str, list[str]] = {}
    current = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("$$"):
            current = stripped.split()[0]
            sections.append(current)
            by_section[current] = []
            continue
        if current:
            by_section[current].append(line.rstrip())
    conc_rows: list[dict[str, object]] = []
    for line in by_section.get("$$CONC", []):
        m = _CONC_ROW_RE.match(line)
        if not m:
            continue
        conc_rows.append({"metabolite": m.group(2), "conc": float(m.group(1))})
    return {
        "sections_order": sections,
        "sections": by_section,
        "concentration_rows": len(conc_rows),
        "concentration_metabolites": [row["metabolite"] for row in conc_rows],
    }
