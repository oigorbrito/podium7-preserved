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
            "blocked": 0,
            "resolverPolicyChanges": 0,
        })
        self.assertEqual(report["unassessedCaseIds"], [])
        self.assertEqual(report["blockedItems"], [])


if __name__ == "__main__":
    unittest.main()
