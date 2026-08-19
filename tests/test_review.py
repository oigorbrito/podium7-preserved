import unittest

from podium7.domain import Conflict, ConflictState
from podium7.identity import MatchOutcome, ResolutionDecision
from podium7.review import ReviewAction, review_conflict, review_evidence, review_identity


class ReviewTests(unittest.TestCase):
    def test_ambiguous_identity_routes_to_review(self):
        decision = ResolutionDecision(MatchOutcome.UNRESOLVED, "insufficient evidence")
        self.assertEqual(review_identity(decision).action, ReviewAction.REVIEW)

    def test_deterministic_identity_routes_automatically(self):
        decision = ResolutionDecision(MatchOutcome.MATCH, "strong deterministic evidence")
        self.assertEqual(review_identity(decision).action, ReviewAction.AUTOMATIC)

    def test_unresolved_conflict_routes_to_review(self):
        conflict = Conflict(id="x", attribute="power", candidate_references=("c1", "c2"), reason="disagreement")
        self.assertEqual(review_conflict(conflict).action, ReviewAction.REVIEW)

    def test_known_valid_non_anomalous_evidence_is_automatic(self):
        self.assertEqual(review_evidence(source_known=True, schema_valid=True).action, ReviewAction.AUTOMATIC)

    def test_new_source_routes_to_review(self):
        self.assertEqual(review_evidence(source_known=False, schema_valid=True).action, ReviewAction.REVIEW)


if __name__ == "__main__":
    unittest.main()
