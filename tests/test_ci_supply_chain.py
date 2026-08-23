from pathlib import Path
import re
import unittest


class CiSupplyChainTests(unittest.TestCase):
    def test_all_github_actions_are_pinned_to_full_commit_sha(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "sequential-tests.yml").read_text(encoding="utf-8")
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, flags=re.MULTILINE)
        self.assertTrue(uses)
        for value in uses:
            with self.subTest(value=value):
                self.assertRegex(value, r"^[^@\s]+@[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
