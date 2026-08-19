import unittest
from datetime import datetime, timezone

from scripts.run_tests_one_by_one import REPORT_SCHEMA, _validate_report


class SequentialTestReportTests(unittest.TestCase):
    def _base_report(self):
        return {
            "schema": REPORT_SCHEMA,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PASS",
            "git_commit": "abc123",
            "python": "3.13.0",
            "python_executable": "python",
            "platform": "test-platform",
            "tests_discovered": 3,
            "tests_passed": 3,
            "failed_test": None,
        }

    def test_valid_pass_report_is_accepted(self):
        _validate_report(self._base_report())

    def test_pass_report_rejects_partial_success(self):
        report = self._base_report()
        report["tests_passed"] = 2
        with self.assertRaises(ValueError):
            _validate_report(report)

    def test_fail_report_rejects_claiming_all_tests_passed(self):
        report = self._base_report()
        report["status"] = "FAIL"
        with self.assertRaises(ValueError):
            _validate_report(report)

    def test_invalid_counts_are_rejected(self):
        report = self._base_report()
        report["tests_passed"] = 4
        with self.assertRaises(ValueError):
            _validate_report(report)

    def test_generated_at_must_be_timezone_aware(self):
        report = self._base_report()
        report["generated_at"] = "2026-08-19T20:00:00"
        with self.assertRaises(ValueError):
            _validate_report(report)


if __name__ == "__main__":
    unittest.main()
