from pathlib import Path
import tempfile
import unittest

from podium7.evidence import content_addressed_ref


class EvidenceReferenceTests(unittest.TestCase):
    def test_same_snapshot_has_stable_content_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.txt"
            path.write_text("vehicle evidence\n", encoding="utf-8")
            first = content_addressed_ref(path)
            second = content_addressed_ref(path)
            self.assertEqual(first, second)
            self.assertTrue(first.startswith("sha256:"))
            self.assertTrue(first.endswith(f"@{path}"))

    def test_changed_snapshot_changes_content_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.txt"
            path.write_text("version one\n", encoding="utf-8")
            first = content_addressed_ref(path)
            path.write_text("version two\n", encoding="utf-8")
            second = content_addressed_ref(path)
            self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
