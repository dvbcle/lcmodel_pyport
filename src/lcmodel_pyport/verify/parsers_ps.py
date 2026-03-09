"""Parser for LCModel .ps output markers."""

from __future__ import annotations

from pathlib import Path


def parse_ps(path: str | Path) -> dict[str, object]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return {"has_crude_model_marker": "CRUDE MODEL" in text}
