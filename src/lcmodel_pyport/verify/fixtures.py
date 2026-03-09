"""Fixture manifest and checksum helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def load_manifest(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_checksums(path: str | Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        digest, rel = stripped.split("  ", 1)
        out[rel.strip()] = digest.strip().upper()
    return out


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().upper()


def verify_checksum(root: str | Path, rel_path: str, expected: str) -> bool:
    actual = sha256_file(Path(root) / rel_path)
    return actual == expected.upper()

