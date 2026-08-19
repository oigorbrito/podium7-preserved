import tempfile
import unittest
from pathlib import Path

from scripts.check_release_readiness import check_release_readiness


class ReleaseReadinessTests(unittest.TestCase):
    def _write_selected_status(self, root: Path) -> None:
        (root / "docs").mkdir()
        (root / "docs" / "LICENSING-STATUS.md").write_text(
            "# Licensing\n\nOwner license selection recorded.\n",
            encoding="utf-8",
        )

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

    def test_spdx_license_without_packaged_license_file_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_selected_status(root)
            (root / "pyproject.toml").write_text(
                "[project]\nname = \"podium7\"\nversion = \"0.1.0\"\nlicense = \"MIT\"\n",
                encoding="utf-8",
            )
            ready, message = check_release_readiness(root)
            self.assertFalse(ready)
            self.assertIn("requires packaged license file", message)

    def test_license_files_pattern_without_match_blocks_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_selected_status(root)
            (root / "pyproject.toml").write_text(
                "[project]\nname = \"podium7\"\nversion = \"0.1.0\"\n"
                "license = \"MIT\"\nlicense-files = [\"LICENSE\"]\n",
                encoding="utf-8",
            )
            ready, message = check_release_readiness(root)
            self.assertFalse(ready)
            self.assertIn("patterns match no files", message)

    def test_owner_declared_license_with_packaged_file_allows_release_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_selected_status(root)
            (root / "LICENSE").write_text("Owner-selected license text.\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project]\nname = \"podium7\"\nversion = \"0.1.0\"\n"
                "license = \"MIT\"\nlicense-files = [\"LICENSE\"]\n",
                encoding="utf-8",
            )
            ready, message = check_release_readiness(root)
            self.assertTrue(ready)
            self.assertEqual(message, "release ready")

    def test_declared_license_file_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_selected_status(root)
            (root / "pyproject.toml").write_text(
                "[project]\nname = \"podium7\"\nversion = \"0.1.0\"\n"
                "license = { file = \"LICENSE\" }\n",
                encoding="utf-8",
            )
            ready, message = check_release_readiness(root)
            self.assertFalse(ready)
            self.assertIn("declared license file does not exist", message)


if __name__ == "__main__":
    unittest.main()
