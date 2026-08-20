import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts.check_package_installation import (
    _single_artifact,
    _stage_source,
    _validate_health,
    _venv_python,
)


class PackageInstallationCheckTests(unittest.TestCase):
    def test_stage_source_copies_only_packaging_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            destination = Path(tmp) / "stage"
            (root / "podium7").mkdir(parents=True)
            (root / "podium7" / "__init__.py").write_text("", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='podium7'\nversion='0.1.0'\n", encoding="utf-8")
            (root / "README.md").write_text("Podium 7\n", encoding="utf-8")
            (root / "unrelated.txt").write_text("do not package\n", encoding="utf-8")

            _stage_source(root, destination)

            self.assertTrue((destination / "pyproject.toml").is_file())
            self.assertTrue((destination / "README.md").is_file())
            self.assertTrue((destination / "podium7" / "__init__.py").is_file())
            self.assertFalse((destination / "unrelated.txt").exists())

    def test_single_artifact_requires_exactly_one_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            with self.assertRaises(RuntimeError):
                _single_artifact(directory, "*.whl")
            (directory / "one.whl").write_text("", encoding="utf-8")
            self.assertEqual(_single_artifact(directory, "*.whl").name, "one.whl")
            (directory / "two.whl").write_text("", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                _single_artifact(directory, "*.whl")

    def test_validate_health_accepts_matching_pass_schema(self):
        payload = {
            "status": "PASS",
            "schema_version": 1,
            "expected_schema_version": 1,
        }
        self.assertEqual(_validate_health(json.dumps(payload)), payload)

    def test_validate_health_rejects_failed_status(self):
        with self.assertRaises(RuntimeError):
            _validate_health(
                json.dumps(
                    {
                        "status": "FAIL",
                        "schema_version": 1,
                        "expected_schema_version": 1,
                    }
                )
            )

    def test_validate_health_rejects_schema_mismatch(self):
        with self.assertRaises(RuntimeError):
            _validate_health(
                json.dumps(
                    {
                        "status": "PASS",
                        "schema_version": 1,
                        "expected_schema_version": 2,
                    }
                )
            )

    def test_venv_python_uses_platform_layout(self):
        environment = Path("example-venv")
        python = _venv_python(environment)
        if os.name == "nt":
            self.assertEqual(python, environment / "Scripts" / "python.exe")
        else:
            self.assertEqual(python, environment / "bin" / "python")


if __name__ == "__main__":
    unittest.main()
