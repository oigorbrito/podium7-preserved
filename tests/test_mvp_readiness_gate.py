from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.check_mvp_exit import REQUIRED_CHECKS, evaluate
from scripts.run_operational_readiness import REPORT_SCHEMA, build_report


class OperationalReadinessTests(unittest.TestCase):
    @patch("scripts.run_operational_readiness.subprocess.run")
    def test_report_runs_required_checks_and_marks_pass(self, run) -> None:
        def completed(argv, **kwargs):
            class Result:
                returncode = 0
                stderr = ""
                stdout = "{}" if "project_facts.py" in argv else "PASS"

            if "project_facts.py" in argv:
                Result.stdout = json.dumps(
                    {
                        "runtime": {"ready": True},
                        "tests_discovered": 1,
                        "catalog_identity_benchmarks": {"case_count": 1},
                    }
                )
            return Result()

        run.side_effect = completed
        report = build_report(Path("."), include_sequential_tests=True, timeout=30)
        self.assertEqual(REPORT_SCHEMA, report["schema"])
        self.assertEqual("PASS", report["status"])
        self.assertEqual(REQUIRED_CHECKS, {item["name"] for item in report["checks"]})


class MvpExitGateTests(unittest.TestCase):
    def readiness(self) -> dict[str, object]:
        checks = [{"name": name, "passed": True} for name in REQUIRED_CHECKS]
        for check in checks:
            if check["name"] == "project-facts":
                check["payload"] = {
                    "runtime": {"ready": True},
                    "tests_discovered": 12,
                    "catalog_identity_benchmarks": {"case_count": 20},
                }
        return {
            "schema": "podium7.operational-readiness.v1",
            "status": "PASS",
            "checks": checks,
        }

    def test_repository_gate_waits_for_official_ci(self) -> None:
        report = evaluate(self.readiness(), ci_green=False)
        self.assertEqual("PENDING", report["status"])
        self.assertEqual("PASS", report["repository_gate"])
        self.assertEqual("PENDING", report["official_ci"])

    def test_gate_passes_only_with_repository_readiness_and_ci(self) -> None:
        report = evaluate(self.readiness(), ci_green=True)
        self.assertEqual("PASS", report["status"])
        self.assertEqual([], report["reasons"])

    def test_missing_required_check_fails_closed(self) -> None:
        readiness = self.readiness()
        readiness["checks"] = [
            item for item in readiness["checks"] if item["name"] != "harness"
        ]
        report = evaluate(readiness, ci_green=True)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("missing required" in reason for reason in report["reasons"]))


if __name__ == "__main__":
    unittest.main()
