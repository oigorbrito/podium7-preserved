from pathlib import Path
import unittest

from podium7.domain import DecisionStatus


CANONICAL_DECISION_LABELS = {
    "EVIDENCE_BACKED",
    "HYPOTHESIS",
    "LOCALLY_VERIFIED",
    "ENGINEERING_CHOICE",
    "UNKNOWN",
}
FORBIDDEN_DECISION_LABELS = {"STANDARD_BACKED"}


class DecisionLabelInvariantTests(unittest.TestCase):
    def test_decision_status_enum_contains_only_canonical_labels(self):
        self.assertEqual({status.value for status in DecisionStatus}, CANONICAL_DECISION_LABELS)

    def test_documentation_does_not_reintroduce_forbidden_labels(self):
        root = Path(__file__).resolve().parents[1]
        violations = []
        for path in sorted((root / "docs").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for label in FORBIDDEN_DECISION_LABELS:
                if label in text:
                    violations.append(f"{path.relative_to(root)}: {label}")
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
