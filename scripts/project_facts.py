from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from typing import Any
import unittest

try:
    from scripts.check_release_readiness import check_release_readiness
except ModuleNotFoundError:  # direct execution from scripts/
    from check_release_readiness import check_release_readiness


REPORT_SCHEMA = "podium7.project-facts.v1"
LABELS = ("MATCH", "NO_MATCH", "REVIEW")


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
    return completed.stdout.strip() or None


def _runtime_health(root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "podium7", "health"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = (completed.stdout or completed.stderr).strip()
    return {"ready": completed.returncode == 0, "message": output}


def _test_count(root: Path) -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(root / "tests"),
        pattern="test_*.py",
        top_level_dir=str(root / "tests"),
    )
    if loader.errors:
        raise ValueError("unittest discovery failed: " + " | ".join(loader.errors))
    return suite.countTestCases()


def _benchmark_facts(root: Path) -> dict[str, Any]:
    datasets: list[dict[str, Any]] = []
    totals = {label: 0 for label in LABELS}
    total_cases = 0
    for path in sorted((root / "benchmarks").glob("catalog_identity_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        cases = payload.get("cases")
        if not isinstance(cases, list):
            raise ValueError(f"benchmark cases must be an array: {path}")
        counts = {label: 0 for label in LABELS}
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError(f"benchmark case must be an object: {path}")
            label = case.get("expected")
            if label not in counts:
                raise ValueError(f"unexpected benchmark label {label!r}: {path}")
            counts[label] += 1
        total_cases += len(cases)
        for label in LABELS:
            totals[label] += counts[label]
        datasets.append(
            {
                "path": str(path.relative_to(root)).replace("\\", "/"),
                "cases": len(cases),
                "labels": counts,
            }
        )
    return {
        "datasets": datasets,
        "dataset_count": len(datasets),
        "case_count": total_cases,
        "labels": totals,
    }


def _scientific_reference_count(root: Path) -> int:
    text = (root / "docs" / "SCIENTIFIC-FOUNDATION.md").read_text(encoding="utf-8")
    return len(re.findall(r"^\|\s*REF-\d+\s*\|", text, flags=re.MULTILINE))


def build_project_facts(root: Path) -> dict[str, Any]:
    release_ready, release_message = check_release_readiness(root)
    return {
        "schema": REPORT_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_head(root),
        "python": platform.python_version(),
        "runtime": _runtime_health(root),
        "tests_discovered": _test_count(root),
        "release": {"ready": release_ready, "message": release_message},
        "catalog_identity_benchmarks": _benchmark_facts(root),
        "scientific_reference_count": _scientific_reference_count(root),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Derive volatile Podium 7 repository facts")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    facts = build_project_facts(root)
    payload = json.dumps(facts, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        target = args.output if args.output.is_absolute() else root / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
        try:
            print(target.relative_to(root))
        except ValueError:
            print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
