from __future__ import annotations

from pathlib import Path
import sys
import tomllib


UNKNOWN_LICENSE_MARKER = "**Status:** `UNKNOWN`"
PRIVATE_PROPRIETARY_MARKER = "**Status:** `PRIVATE_PROPRIETARY`"


def _matched_license_files(root: Path, project: dict[str, object]) -> tuple[bool, str | None]:
    license_value = project.get("license")
    license_files = project.get("license-files")

    if license_value is None and license_files is None:
        return False, "release blocked: package metadata does not declare a license"

    if isinstance(license_value, dict):
        license_file = license_value.get("file")
        license_text = license_value.get("text")
        if license_file is not None:
            if not isinstance(license_file, str) or not license_file.strip():
                return False, "release blocked: package license file declaration is invalid"
            path = root / license_file
            if not path.is_file():
                return False, f"release blocked: declared license file does not exist: {license_file}"
            if not path.read_text(encoding="utf-8").strip():
                return False, f"release blocked: declared license file is empty: {license_file}"
        elif license_text is not None:
            if not isinstance(license_text, str) or not license_text.strip():
                return False, "release blocked: package license text declaration is invalid"
        else:
            return False, "release blocked: package license declaration is invalid"
    elif license_value is not None and not isinstance(license_value, str):
        return False, "release blocked: package license declaration is invalid"
    elif isinstance(license_value, str) and not license_value.strip():
        return False, "release blocked: package license declaration is invalid"

    if license_files is not None:
        if (
            not isinstance(license_files, list)
            or not license_files
            or not all(isinstance(pattern, str) and pattern.strip() for pattern in license_files)
        ):
            return False, "release blocked: package license-files declaration is invalid"

        matches = {
            path
            for pattern in license_files
            for path in root.glob(pattern)
            if path.is_file()
        }
        if not matches:
            return False, "release blocked: package license-files patterns match no files"
        for path in matches:
            if not path.read_text(encoding="utf-8").strip():
                relative = path.relative_to(root)
                return False, f"release blocked: matched license file is empty: {relative}"

    if isinstance(license_value, str) and license_files is None:
        return False, "release blocked: SPDX license declaration requires packaged license file(s)"

    return True, None


def check_release_readiness(root: Path) -> tuple[bool, str]:
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    licensing_status = (root / "docs" / "LICENSING-STATUS.md").read_text(encoding="utf-8")

    if PRIVATE_PROPRIETARY_MARKER in licensing_status:
        return False, "release blocked: software is private/proprietary and no public distribution license is granted"
    if UNKNOWN_LICENSE_MARKER in licensing_status:
        return False, "release blocked: software license status is UNKNOWN"

    coherent, message = _matched_license_files(root, project)
    if not coherent:
        return False, message or "release blocked: package license metadata is incoherent"

    return True, "release ready"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ready, message = check_release_readiness(root)
    print(message)
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
