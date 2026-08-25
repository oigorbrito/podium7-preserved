from pathlib import Path
import json
import unittest

from podium7.review_disposition import evaluate_review_dispositions


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
ENRICHMENT_V3 = ROOT / "benchmarks" / "source_backed_enrichment_v3.json"
DISPOSITIONS = ROOT / "benchmarks" / "review_disposition_v2.json"
EXPECTED_REVIEW_KEYS = {
    ("review-ford-mustang-variant-missing", "right"),
    ("review-porsche-911-partial-variant-label", "left"),
    ("review-porsche-911-partial-variant-label", "right"),
    ("review-bmw-g20-generic-vs-330i-label", "left"),
    ("review-bmw-g20-generic-vs-330i-label", "right"),
    ("br-review-corolla-cross-xrx-hybrid-missing-variant", "right"),
    ("br-review-onix-premier-missing-variant", "right"),
    ("br-review-tcross-250-tsi-missing-variant", "right"),
    ("br-review-shared-fipe-code-alone", "left"),
    ("br-review-shared-fipe-code-alone", "right"),
    ("br-hard-review-tcross-highline-model-year-present-one-side", "right"),
    ("br-hard-no-match-corolla-altis-hybrid-my25-vs-my26", "left"),
    ("br-hard-no-match-corolla-altis-hybrid-my25-vs-my26", "right"),
}


class ProductionReviewExhaustionV2Tests(unittest.TestCase):
    def test_current_v3_review_queue_is_fully_assessed(self) -> None:
        report = evaluate_review_dispositions(DATASETS, ENRICHMENT_V3, DISPOSITIONS)

        self.assertEqual(report["summary"]["openReviews"], 13)
        if report["unassessedItems"]:
            self.fail(json.dumps(report["unassessedItems"], sort_keys=True))
        self.assertEqual(report["summary"], {
            "openReviews": 13,
            "durableHumanReview": 13,
            "unassessed": 0,
            "unusedDispositions": 0,
            "blocked": 0,
            "resolverPolicyChanges": 0,
        })
        self.assertEqual(report["unassessedCaseIds"], [])
        self.assertEqual(report["unusedDispositionCaseIds"], [])
        self.assertEqual(report["unassessedReviewKeys"], [])
        self.assertEqual(report["unusedDispositionKeys"], [])
        self.assertEqual(report["blockedItems"], [])
        self.assertEqual(
            {
                (item["caseId"], item["side"])
                for item in report["durableHumanReviewItems"]
            },
            EXPECTED_REVIEW_KEYS,
        )


if __name__ == "__main__":
    unittest.main()
