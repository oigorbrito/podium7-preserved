from __future__ import annotations

from pathlib import Path
import sys
import tomllib


UNKNOWN_LICENSE_MARKER = "**Status:** `UNKNOWN`"


def check_release_readiness(root: Path) -> tuple[bool, str]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    licensing_status = (root / "docs" / "LICENSING-STATUS.md").read_text(encoding="utf-8")

    if UNKNOWN_LICENSE_MARKER in licensing_status:
        return False, "release blocked: software license status is UNKNOWN"
    if "license" not in project and "license-files" not in project:
        return False, "release blocked: package metadata does not declare a license"
    return True, "release ready"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ready, message = check_release_readiness(root)
    print(message)
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
