from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.check_mvp_exit import REQUIRED_CHECKS, evaluate, verify_independent_evidence
from scripts.run_operational_readiness import REPORT_SCHEMA, build_report


class OperationalReadinessTests(unittest.TestCase):
    @patch("scripts.run_operational_readiness.subprocess.run")
    def test_report_runs_required_checks_and_marks_pass(self, run) -> None:
        def completed(argv, **kwargs):
            class Result:
                returncode = 0
                stderr = ""
                stdout = "PASS"

            if any(arg.endswith("run_catalog_identity_benchmark.py") for arg in argv):
                Result.stdout = json.dumps(
                    {
                        "totalCases": 3,
                        "metrics": {
                            "correct": 3,
                            "falseMergeCount": 0,
                            "ambiguousOvercommitCount": 0,
                        },
                    }
                )
            elif any(arg.endswith("project_facts.py") for arg in argv):
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

    @patch("scripts.run_operational_readiness.subprocess.run")
    def test_benchmark_regression_fails_readiness_even_with_zero_exit(self, run) -> None:
        class Result:
            returncode = 0
            stderr = ""
            stdout = "PASS"

        def completed(argv, **kwargs):
            result = Result()
            if any(arg.endswith("run_catalog_identity_benchmark.py") for arg in argv):
                result.stdout = json.dumps(
                    {
                        "totalCases": 3,
                        "metrics": {
                            "correct": 2,
                            "falseMergeCount": 1,
                            "ambiguousOvercommitCount": 0,
                        },
                    }
                )
            elif any(arg.endswith("project_facts.py") for arg in argv):
                result.stdout = json.dumps(
                    {
                        "runtime": {"ready": True},
                        "tests_discovered": 1,
                        "catalog_identity_benchmarks": {"case_count": 1},
                    }
                )
            return result

        run.side_effect = completed
        report = build_report(Path("."), include_sequential_tests=True, timeout=30)
        self.assertEqual("FAIL", report["status"])
        benchmark = next(item for item in report["checks"] if item["name"] == "catalog-identity-golden")
        self.assertFalse(benchmark["passed"])
        self.assertEqual("catalog benchmark safety metrics are not fully green", benchmark.get("error"))


class MvpExitGateTests(unittest.TestCase):
    COMMIT = "a" * 40

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

    def independent_evidence(self) -> dict[str, object]:
        return {
            "schema": "podium7.independent-validation.v1",
            "status": "PASS",
            "commit_sha": self.COMMIT,
            "clean_worktree": True,
            "readiness_status": "PASS",
            "sequential_tests_passed": True,
        }

    def test_repository_gate_waits_for_execution_validation(self) -> None:
        report = evaluate(self.readiness())
        self.assertEqual("PENDING", report["status"])
        self.assertEqual("PASS", report["repository_gate"])
        self.assertEqual("PENDING", report["execution_validation"])
        self.assertEqual("none", report["validation_source"])

    def test_gate_passes_with_verified_github_actions(self) -> None:
        report = evaluate(self.readiness(), ci_green=True)
        self.assertEqual("PASS", report["status"])
        self.assertEqual("PASS", report["execution_validation"])
        self.assertEqual("github-actions", report["validation_source"])
        self.assertEqual("PASS", report["official_ci"])
        self.assertEqual([], report["reasons"])

    def test_gate_passes_with_verified_independent_equivalent_validation(self) -> None:
        verified, reasons = verify_independent_evidence(
            self.independent_evidence(),
            expected_commit=self.COMMIT,
        )
        self.assertTrue(verified)
        report = evaluate(
            self.readiness(),
            independent_validation=verified,
            independent_reasons=reasons,
        )
        self.assertEqual("PASS", report["status"])
        self.assertEqual("independent-equivalent", report["validation_source"])
        self.assertEqual("PENDING", report["official_ci"])

    def test_independent_validation_rejects_wrong_commit(self) -> None:
        verified, reasons = verify_independent_evidence(
            self.independent_evidence(),
            expected_commit="b" * 40,
        )
        self.assertFalse(verified)
        self.assertIn("independent validation commit does not match current candidate", reasons)

    def test_independent_validation_rejects_dirty_worktree(self) -> None:
        evidence = self.independent_evidence()
        evidence["clean_worktree"] = False
        verified, reasons = verify_independent_evidence(evidence, expected_commit=self.COMMIT)
        self.assertFalse(verified)
        self.assertIn("independent validation did not use a clean tracked worktree", reasons)

    def test_missing_required_check_fails_closed_even_with_validation(self) -> None:
        readiness = self.readiness()
        readiness["checks"] = [
            item for item in readiness["checks"] if item["name"] != "harness"
        ]
        report = evaluate(readiness, independent_validation=True)
        self.assertEqual("FAIL", report["status"])
        self.assertTrue(any("missing required" in reason for reason in report["reasons"]))


if __name__ == "__main__":
    unittest.main()
