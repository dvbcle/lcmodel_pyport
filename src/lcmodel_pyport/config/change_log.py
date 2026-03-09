"""Effective control-change extraction."""

from __future__ import annotations

from lcmodel_pyport.config.control_parser import parse_assignments


def extract_effective_changes(text: str) -> list[str]:
    """Return final effective assignments in input order (last assignment kept)."""
    last_seen: dict[str, str] = {}
    order: list[str] = []
    for assignment in parse_assignments(text):
        if assignment.key not in last_seen:
            order.append(assignment.key)
        last_seen[assignment.key] = assignment.raw_value.rstrip(",")
    return [f"{key}={last_seen[key]}" for key in order]

