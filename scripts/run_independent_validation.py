from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_operational_readiness import build_report


REPORT_SCHEMA = "podium7.independent-validation.v1"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def build_validation(root: Path, *, timeout: int) -> dict[str, object]:
    commit_sha = _git(root, "rev-parse", "HEAD")
    tracked_changes = _git(root, "status", "--porcelain", "--untracked-files=no")
    clean_worktree = tracked_changes == ""

    if clean_worktree:
        readiness = build_report(root, include_sequential_tests=True, timeout=timeout)
    else:
        readiness = {
            "schema": "podium7.operational-readiness.v1",
            "status": "FAIL",
            "checks": [],
        }

    checks = readiness.get("checks") if isinstance(readiness, dict) else None
    sequential = None
    if isinstance(checks, list):
        sequential = next(
            (item for item in checks if isinstance(item, dict) and item.get("name") == "sequential-tests"),
            None,
        )
    sequential_tests_passed = isinstance(sequential, dict) and sequential.get("passed") is True
    readiness_status = readiness.get("status") if isinstance(readiness, dict) else "FAIL"
    passed = clean_worktree and readiness_status == "PASS" and sequential_tests_passed

    return {
        "schema": REPORT_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed else "FAIL",
        "commit_sha": commit_sha,
        "clean_worktree": clean_worktree,
        "readiness_status": readiness_status,
        "sequential_tests_passed": sequential_tests_passed,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
        },
        "readiness": readiness,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Produce independent-equivalent execution evidence for the exact Podium 7 checkout"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    try:
        report = build_validation(ROOT, timeout=args.timeout)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"schema": REPORT_SCHEMA, "status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2

    target = args.output if args.output.is_absolute() else ROOT / args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(target)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
