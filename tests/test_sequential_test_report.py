import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts.run_tests_one_by_one import (
    REPORT_SCHEMA,
    _discover_test_ids,
    _validate_report,
    _write_report,
    main,
)


class SequentialTestReportTests(unittest.TestCase):
    def _base_report(self):
        return {
            "schema": REPORT_SCHEMA,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "PASS",
            "git_commit": "a" * 40,
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

    def test_extra_report_field_is_rejected(self):
        report = self._base_report()
        report["unexpected"] = True
        with self.assertRaises(ValueError):
            _validate_report(report)

    def test_missing_report_field_is_rejected(self):
        report = self._base_report()
        del report["platform"]
        with self.assertRaises(ValueError):
            _validate_report(report)

    def test_malformed_git_commit_is_rejected(self):
        report = self._base_report()
        report["git_commit"] = "abc123"
        with self.assertRaises(ValueError):
            _validate_report(report)

    def test_duplicate_test_identifier_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tests_dir = Path(tmp)
            (tests_dir / "test_duplicate.py").write_text(
                "import unittest\n\n"
                "class DuplicateTests(unittest.TestCase):\n"
                "    def test_same(self):\n"
                "        pass\n"
                "    def test_same(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                _discover_test_ids(tests_dir)

    def test_alias_testcase_is_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            tests_dir = Path(tmp)
            (tests_dir / "test_alias.py").write_text(
                "import unittest\n\n"
                "Case = unittest.TestCase\n\n"
                "class AliasTests(Case):\n"
                "    def test_alias(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            self.assertEqual(
                _discover_test_ids(tests_dir),
                ["test_alias.AliasTests.test_alias"],
            )

    def test_indirect_testcase_inheritance_is_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            tests_dir = Path(tmp)
            (tests_dir / "test_indirect.py").write_text(
                "import unittest\n\n"
                "class BaseTests(unittest.TestCase):\n"
                "    pass\n\n"
                "class IndirectTests(BaseTests):\n"
                "    def test_indirect(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            self.assertEqual(
                _discover_test_ids(tests_dir),
                ["test_indirect.IndirectTests.test_indirect"],
            )

    def test_report_write_is_atomic_and_leaves_no_temp_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real_replace = os.replace
            with mock.patch("scripts.run_tests_one_by_one.os.replace", wraps=real_replace) as replace:
                _write_report(root, total=1, passed=1, status="PASS")

            target = root / "artifacts" / "test-report.json"
            self.assertTrue(target.is_file())
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["status"], "PASS")
            replace.assert_called_once()
            source, destination = replace.call_args.args
            self.assertNotEqual(Path(source), Path(destination))
            self.assertEqual(Path(destination), target)
            self.assertEqual(list(target.parent.glob(".test-report-*.tmp")), [])

    def test_discovery_interrupt_writes_fail_report(self):
        with (
            mock.patch("scripts.run_tests_one_by_one._discover_test_ids", side_effect=KeyboardInterrupt),
            mock.patch("scripts.run_tests_one_by_one._write_report") as write_report,
        ):
            result = main()

        self.assertEqual(result, 130)
        write_report.assert_called_once()
        self.assertEqual(write_report.call_args.kwargs, {"total": 0, "passed": 0, "status": "FAIL"})

    def test_test_interrupt_writes_current_failure_report(self):
        test_id = "test_example.ExampleTests.test_example"
        with (
            mock.patch("scripts.run_tests_one_by_one._discover_test_ids", return_value=[test_id]),
            mock.patch("scripts.run_tests_one_by_one.subprocess.run", side_effect=KeyboardInterrupt),
            mock.patch("scripts.run_tests_one_by_one._write_report") as write_report,
        ):
            result = main()

        self.assertEqual(result, 130)
        write_report.assert_called_once()
        self.assertEqual(
            write_report.call_args.kwargs,
            {"total": 1, "passed": 0, "status": "FAIL", "failed_test": test_id},
        )

    def test_subprocess_launch_error_writes_current_failure_report(self):
        test_id = "test_example.ExampleTests.test_example"
        with (
            mock.patch("scripts.run_tests_one_by_one._discover_test_ids", return_value=[test_id]),
            mock.patch("scripts.run_tests_one_by_one.subprocess.run", side_effect=OSError("launch failed")),
            mock.patch("scripts.run_tests_one_by_one._write_report") as write_report,
        ):
            result = main()

        self.assertEqual(result, 2)
        write_report.assert_called_once()
        self.assertEqual(
            write_report.call_args.kwargs,
            {"total": 1, "passed": 0, "status": "FAIL", "failed_test": test_id},
        )


if __name__ == "__main__":
    unittest.main()
