from __future__ import annotations

import re
import subprocess
from pathlib import Path

BLOCKED_BASENAMES = {".env", ".env.local", ".env.production", "credentials.json", "service-account.json"}
BLOCKED_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
PATTERNS = (
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("GITHUB_TOKEN", re.compile(r"gh" + r"[pousr]_[A-Za-z0-9_]{30,}")),
    ("GITHUB_FINE_GRAINED_TOKEN", re.compile(r"github" + r"_pat_[A-Za-z0-9_]{40,}")),
    ("AWS_ACCESS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("OPENAI_API_KEY", re.compile(r"sk" + r"-(?:proj-)?[A-Za-z0-9_-]{24,}")),
)


def tracked_files(root: Path) -> tuple[Path, ...]:
    output = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True
    ).stdout
    return tuple(root / item.decode() for item in output.split(b"\0") if item)


def inspect_path(path: Path, root: Path) -> list[str]:
    relative = path.relative_to(root).as_posix()
    findings: list[str] = []
    name = path.name.casefold()
    if name in BLOCKED_BASENAMES or path.suffix.casefold() in BLOCKED_SUFFIXES:
        findings.append(f"BLOCKED_FILENAME:{relative}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        findings.append(f"READ_ERROR:{relative}:{exc}")
        return findings
    if b"\x00" in data:
        return findings
    text = data.decode("utf-8", errors="replace")
    for label, pattern in PATTERNS:
        if pattern.search(text):
            findings.append(f"{label}:{relative}")
    return findings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings: list[str] = []
    for path in tracked_files(root):
        findings.extend(inspect_path(path, root))
    if findings:
        for finding in findings:
            print(finding)
        print(f"SECRET_HYGIENE FAIL findings={len(findings)}")
        return 1
    print("SECRET_HYGIENE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
