"""Snapshot save/restore primitives for best-solution state."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    state: dict[str, object]


def save_snapshot(state: dict[str, object]) -> Snapshot:
    return Snapshot(state=deepcopy(state))


def restore_snapshot(snapshot: Snapshot) -> dict[str, object]:
    return deepcopy(snapshot.state)
