from pathlib import Path
import tempfile
import unittest

from podium7.evidence import content_addressed_ref, verify_content_addressed_ref


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

    def test_unchanged_snapshot_verifies(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.txt"
            path.write_text("stable evidence\n", encoding="utf-8")
            reference = content_addressed_ref(path)
            self.assertTrue(verify_content_addressed_ref(reference))

    def test_changed_snapshot_fails_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.txt"
            path.write_text("before\n", encoding="utf-8")
            reference = content_addressed_ref(path)
            path.write_text("after\n", encoding="utf-8")
            self.assertFalse(verify_content_addressed_ref(reference))

    def test_malformed_or_missing_reference_fails_verification(self):
        self.assertFalse(verify_content_addressed_ref("not-a-content-reference"))
        self.assertFalse(verify_content_addressed_ref("sha256:" + "0" * 64 + "@/definitely/missing/podium7.snapshot"))


if __name__ == "__main__":
    unittest.main()
