from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPORT_SCHEMA = "podium7.mvp-exit-gate.v1"
READINESS_SCHEMA = "podium7.operational-readiness.v1"
REQUIRED_CHECKS = {
    "runtime-health",
    "harness",
    "repository-secrets",
    "package-installation",
    "catalog-identity-golden",
    "project-facts",
    "sequential-tests",
}


def evaluate(readiness: dict[str, Any], *, ci_green: bool) -> dict[str, Any]:
    reasons: list[str] = []
    if readiness.get("schema") != READINESS_SCHEMA:
        reasons.append("invalid operational-readiness schema")

    checks = readiness.get("checks")
    by_name: dict[str, dict[str, Any]] = {}
    if not isinstance(checks, list):
        reasons.append("operational-readiness checks must be an array")
    else:
        for check in checks:
            if isinstance(check, dict) and isinstance(check.get("name"), str):
                by_name[check["name"]] = check

    missing = sorted(REQUIRED_CHECKS - set(by_name))
    if missing:
        reasons.append("missing required readiness checks: " + ", ".join(missing))

    failed = sorted(
        name for name in REQUIRED_CHECKS if name in by_name and by_name[name].get("passed") is not True
    )
    if failed:
        reasons.append("failed readiness checks: " + ", ".join(failed))

    facts = by_name.get("project-facts", {}).get("payload")
    if not isinstance(facts, dict):
        reasons.append("project-facts check did not expose a JSON payload")
    else:
        runtime = facts.get("runtime")
        if not isinstance(runtime, dict) or runtime.get("ready") is not True:
            reasons.append("project runtime is not ready")
        tests_discovered = facts.get("tests_discovered")
        if not isinstance(tests_discovered, int) or tests_discovered <= 0:
            reasons.append("no repository tests were discovered")
        benchmarks = facts.get("catalog_identity_benchmarks")
        if not isinstance(benchmarks, dict) or not isinstance(benchmarks.get("case_count"), int) or benchmarks["case_count"] <= 0:
            reasons.append("catalog identity benchmark coverage is empty")

    repository_gate_passed = not reasons
    overall_passed = repository_gate_passed and ci_green
    if repository_gate_passed and not ci_green:
        reasons.append("official merge-candidate GitHub Actions evidence is not green")

    return {
        "schema": REPORT_SCHEMA,
        "status": "PASS" if overall_passed else "PENDING" if repository_gate_passed else "FAIL",
        "repository_gate": "PASS" if repository_gate_passed else "FAIL",
        "official_ci": "PASS" if ci_green else "PENDING",
        "public_release_required": False,
        "reasons": reasons,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the Podium 7 private-MVP exit gate from an operational-readiness report"
    )
    parser.add_argument("readiness_report", type=Path)
    parser.add_argument(
        "--ci-green",
        action="store_true",
        help="attest only after independently verifying executable green repository CI on the merge candidate",
    )
    args = parser.parse_args(argv)

    try:
        readiness = json.loads(args.readiness_report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": REPORT_SCHEMA, "status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 2

    report = evaluate(readiness, ci_green=args.ci_green)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if report["status"] == "PASS":
        return 0
    if report["status"] == "PENDING":
        return 3
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
