import tempfile
import unittest
from pathlib import Path

from scripts.check_release_readiness import check_release_readiness


class ReleaseReadinessTests(unittest.TestCase):
    def test_unknown_license_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "LICENSING-STATUS.md").write_text(
                "# Licensing\n\n**Status:** `UNKNOWN`\n",
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                "[project]\nname = \"podium7\"\nversion = \"0.1.0\"\n",
                encoding="utf-8",
            )
            ready, message = check_release_readiness(root)
            self.assertFalse(ready)
            self.assertIn("license status is UNKNOWN", message)

    def test_owner_declared_license_allows_release_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "LICENSING-STATUS.md").write_text(
                "# Licensing\n\nOwner license selection recorded.\n",
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                "[project]\nname = \"podium7\"\nversion = \"0.1.0\"\nlicense = \"MIT\"\n",
                encoding="utf-8",
            )
            ready, message = check_release_readiness(root)
            self.assertTrue(ready)
            self.assertEqual(message, "release ready")


if __name__ == "__main__":
    unittest.main()
