from __future__ import annotations

import hashlib
from pathlib import Path


def content_addressed_ref(path: str | Path) -> str:
    """Return a stable SHA-256 reference that retains the local snapshot path."""

    snapshot = Path(path)
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    return f"sha256:{digest}@{snapshot}"
