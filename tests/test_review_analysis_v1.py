from pathlib import Path
import unittest

from podium7.catalog_quality import analyze_review_cases, evaluate_identity_quality


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ReviewAnalysisV1Tests(unittest.TestCase):
    def test_all_measured_reviews_have_known_safe_causes(self) -> None:
        analysis = analyze_review_cases(evaluate_identity_quality(DATASETS))

        self.assertEqual(analysis["totalReviews"], 11)
        self.assertEqual(analysis["unknownCauseCount"], 0)
        self.assertEqual(analysis["unexpectedReviewCount"], 0)
        self.assertGreater(analysis["causeCounts"].get("MISSING_IDENTITY_EVIDENCE", 0), 0)
        self.assertTrue(all(case["expected"] == "REVIEW" for case in analysis["cases"]))


if __name__ == "__main__":
    unittest.main()
