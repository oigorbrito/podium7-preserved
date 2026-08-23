from pathlib import Path
import unittest


class PythonSupportCiTests(unittest.TestCase):
    def test_declared_minimum_python_has_dedicated_ci_lane(self):
        root = Path(__file__).resolve().parents[1]
        pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
        workflow = (root / ".github" / "workflows" / "sequential-tests.yml").read_text(encoding="utf-8")
        self.assertIn('requires-python = ">=3.11"', pyproject)
        self.assertIn("minimum-python:", workflow)
        self.assertIn('python-version: "3.11"', workflow)
        self.assertIn("Run every test in isolation on Python 3.11", workflow)


if __name__ == "__main__":
    unittest.main()
