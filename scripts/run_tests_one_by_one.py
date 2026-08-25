from __future__ import annotations

import ast
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterator
import unittest


REPORT_SCHEMA = "podium7.sequential-test-report.v1"
REPORT_KEYS = {
    "schema",
    "generated_at",
    "status",
    "git_commit",
    "python",
    "python_executable",
    "platform",
    "tests_discovered",
    "tests_passed",
    "failed_test",
}
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _reject_duplicate_test_methods(tests_dir: Path) -> None:
    for path in sorted(tests_dir.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            seen: set[str] = set()
            for member in node.body:
                if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if not member.name.startswith("test_"):
                    continue
                test_id = f"{path.stem}.{node.name}.{member.name}"
                if member.name in seen:
                    raise ValueError(f"duplicate test identifier: {test_id}")
                seen.add(member.name)


def _iter_tests(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_tests(item)
        else:
            yield item


def _discover_test_ids(tests_dir: Path) -> list[str]:
    _reject_duplicate_test_methods(tests_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(tests_dir),
        pattern="test_*.py",
        top_level_dir=str(tests_dir),
    )
    if loader.errors:
        raise ValueError("unittest discovery failed: " + " | ".join(loader.errors))

    test_ids: list[str] = []
    seen: set[str] = set()
    for test in _iter_tests(suite):
        test_id = test.id()
        if test_id in seen:
            raise ValueError(f"duplicate test identifier: {test_id}")
        seen.add(test_id)
        test_ids.append(test_id)
    return sorted(test_ids)


def _git_head(root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    head = completed.stdout.strip()
    return head or None


def _validate_report(report: dict[str, Any]) -> None:
    if set(report) != REPORT_KEYS:
        missing = sorted(REPORT_KEYS - set(report))
        extra = sorted(set(report) - REPORT_KEYS)
        raise ValueError(f"unexpected test report fields; missing={missing}, extra={extra}")

    if report.get("schema") != REPORT_SCHEMA:
        raise ValueError("unexpected test report schema")
    status = report.get("status")
    if status not in {"PASS", "FAIL"}:
        raise ValueError("test report status must be PASS or FAIL")

    total = report.get("tests_discovered")
    passed = report.get("tests_passed")
    if type(total) is not int or total < 0:
        raise ValueError("tests_discovered must be a non-negative integer")
    if type(passed) is not int or passed < 0 or passed > total:
        raise ValueError("tests_passed must be between zero and tests_discovered")

    failed_test = report.get("failed_test")
    if failed_test is not None and (not isinstance(failed_test, str) or not failed_test.strip()):
        raise ValueError("failed_test must be a non-empty string or null")

    if status == "PASS":
        if total == 0 or passed != total or failed_test is not None:
            raise ValueError("PASS report requires all discovered tests to pass")
    else:
        if passed == total and total > 0:
            raise ValueError("FAIL report cannot claim all discovered tests passed")

    generated_at = report.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at.strip():
        raise ValueError("generated_at is required")
    parsed = datetime.fromisoformat(generated_at)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware")

    for key in ("python", "python_executable", "platform"):
        value = report.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} is required")

    git_commit = report.get("git_commit")
    if git_commit is not None and (not isinstance(git_commit, str) or GIT_SHA_RE.fullmatch(git_commit) is None):
        raise ValueError("git_commit must be a 40-character lowercase hexadecimal SHA or null")


def _build_report(
    root: Path,
    *,
    total: int,
    passed: int,
    status: str,
    failed_test: str | None = None,
) -> dict[str, Any]:
    report = {
        "schema": REPORT_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "git_commit": _git_head(root),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "tests_discovered": total,
        "tests_passed": passed,
        "failed_test": failed_test,
    }
    _validate_report(report)
    return report


def _write_report(
    root: Path,
    *,
    total: int,
    passed: int,
    status: str,
    failed_test: str | None = None,
) -> None:
    report_dir = root / "artifacts"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = _build_report(
        root,
        total=total,
        passed=passed,
        status=status,
        failed_test=failed_test,
    )
    target = report_dir / "test-report.json"
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=report_dir,
            prefix=".test-report-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, target)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tests_dir = root / "tests"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        test_ids = _discover_test_ids(tests_dir)
    except KeyboardInterrupt:
        _write_report(root, total=0, passed=0, status="FAIL")
        print("FAIL — test discovery interrupted", flush=True)
        return 130
    except (OSError, SyntaxError, ValueError) as exc:
        _write_report(root, total=0, passed=0, status="FAIL")
        print(f"FAIL — test discovery error: {exc}")
        return 2

    if not test_ids:
        _write_report(root, total=0, passed=0, status="FAIL")
        print("FAIL — no tests discovered")
        return 2

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    pythonpath_parts = [str(root), str(tests_dir)]
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    total = len(test_ids)
    passed = 0
    for index, test_id in enumerate(test_ids, start=1):
        print(f"[{index}/{total}] RUN {test_id}", flush=True)
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "unittest", test_id],
                cwd=root,
                env=env,
                check=False,
            )
        except KeyboardInterrupt:
            _write_report(
                root,
                total=total,
                passed=passed,
                status="FAIL",
                failed_test=test_id,
            )
            print(f"[{index}/{total}] INTERRUPTED {test_id}", flush=True)
            return 130
        except OSError as exc:
            _write_report(
                root,
                total=total,
                passed=passed,
                status="FAIL",
                failed_test=test_id,
            )
            print(f"[{index}/{total}] ERROR {test_id}: {exc}", flush=True)
            return 2
        if completed.returncode != 0:
            _write_report(
                root,
                total=total,
                passed=passed,
                status="FAIL",
                failed_test=test_id,
            )
            print(f"[{index}/{total}] FAIL {test_id}", flush=True)
            return completed.returncode
        passed += 1
        print(f"[{index}/{total}] PASS {test_id}", flush=True)

    _write_report(root, total=total, passed=passed, status="PASS")
    print(f"PASS — {total}/{total} tests executed one by one", flush=True)
    print("REPORT — artifacts/test-report.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
