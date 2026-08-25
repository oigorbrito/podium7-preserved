from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


REPORT_SCHEMA = "podium7.operational-readiness.v1"


def _run_check(root: Path, name: str, argv: list[str], timeout: int) -> dict[str, Any]:
    completed = subprocess.run(
        argv,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    result: dict[str, Any] = {
        "name": name,
        "command": argv,
        "passed": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }
    if stdout.startswith("{"):
        try:
            result["payload"] = json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return result


def build_report(root: Path, *, include_sequential_tests: bool, timeout: int) -> dict[str, Any]:
    python = sys.executable
    commands: list[tuple[str, list[str]]] = [
        ("runtime-health", [python, "-m", "podium7", "health"]),
        ("harness", [python, "scripts/check_harness.py"]),
        ("repository-secrets", [python, "scripts/check_repository_secrets.py"]),
        ("package-installation", [python, "scripts/check_package_installation.py"]),
        (
            "catalog-identity-golden",
            [python, "scripts/run_catalog_identity_benchmark.py", "--compact"],
        ),
        ("project-facts", [python, "scripts/project_facts.py"]),
    ]
    if include_sequential_tests:
        commands.append(("sequential-tests", [python, "scripts/run_tests_one_by_one.py"]))

    checks: list[dict[str, Any]] = []
    for name, argv in commands:
        try:
            checks.append(_run_check(root, name, argv, timeout))
        except subprocess.TimeoutExpired as exc:
            checks.append(
                {
                    "name": name,
                    "command": argv,
                    "passed": False,
                    "returncode": None,
                    "stdout": exc.stdout or "",
                    "stderr": exc.stderr or "",
                    "error": f"timeout after {timeout}s",
                }
            )

    passed = all(check["passed"] for check in checks)
    return {
        "schema": REPORT_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the deterministic private-operational readiness checks for Podium 7"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skip-sequential-tests", action="store_true")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    report = build_report(
        root,
        include_sequential_tests=not args.skip_sequential_tests,
        timeout=args.timeout,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        target = args.output if args.output.is_absolute() else root / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
        print(target)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
