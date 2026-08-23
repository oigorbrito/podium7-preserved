from pathlib import Path
import unittest


class RepositoryCollaborationHygieneTests(unittest.TestCase):
    def test_collaboration_policy_files_exist_and_are_linked(self):
        root = Path(__file__).resolve().parents[1]
        required = ("CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md")
        readme = (root / "README.md").read_text(encoding="utf-8")
        for name in required:
            with self.subTest(name=name):
                path = root / name
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 100)
                self.assertIn(f"]({name})", readme)


if __name__ == "__main__":
    unittest.main()
