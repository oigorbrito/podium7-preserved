import tomllib
import unittest
from pathlib import Path


class PackagingMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.payload = tomllib.loads((cls.root / "pyproject.toml").read_text(encoding="utf-8"))

    def test_project_metadata_is_minimal_and_dependency_free(self):
        project = self.payload["project"]
        self.assertEqual(project["name"], "podium7")
        self.assertEqual(project["version"], "0.1.0")
        self.assertEqual(project["requires-python"], ">=3.11")
        self.assertEqual(project["dependencies"], [])

    def test_build_backend_is_explicit(self):
        build = self.payload["build-system"]
        self.assertEqual(build["build-backend"], "setuptools.build_meta")
        self.assertIn("setuptools>=68", build["requires"])

    def test_only_podium7_package_is_declared(self):
        self.assertEqual(self.payload["tool"]["setuptools"]["packages"], ["podium7"])

    def test_packaging_does_not_claim_public_license_while_private(self):
        project = self.payload["project"]
        self.assertNotIn("license", project)
        self.assertNotIn("license-files", project)
        self.assertFalse((self.root / "LICENSE").exists())
        status = (self.root / "docs" / "LICENSING-STATUS.md").read_text(encoding="utf-8")
        self.assertIn("**Status:** `PRIVATE_PROPRIETARY`", status)
        self.assertIn("No public software license is granted", status)


if __name__ == "__main__":
    unittest.main()
