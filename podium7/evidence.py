from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
import re


_REF_PATTERN = re.compile(r"^sha256:([0-9a-f]{64})@(.+)$")


def content_addressed_ref(path: str | Path) -> str:
    """Return a stable SHA-256 reference that retains the local snapshot path."""

    snapshot = Path(path)
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    return f"sha256:{digest}@{snapshot}"


def verify_content_addressed_ref(reference: str) -> bool:
    """Verify that a content-addressed reference still matches its snapshot."""

    match = _REF_PATTERN.fullmatch(reference)
    if match is None:
        return False

    expected_digest, path_text = match.groups()
    snapshot = Path(path_text)
    if not snapshot.is_file():
        return False

    actual_digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    return hmac.compare_digest(actual_digest, expected_digest)
