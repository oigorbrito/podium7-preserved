from pathlib import Path
import json
import tempfile
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

    def test_case_disposition_does_not_cover_an_unassessed_side(self) -> None:
        payload = json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
        decision = next(
            item
            for item in payload["decisions"]
            if item["caseId"] == "review-porsche-911-partial-variant-label"
        )
        right_evidence_id = decision["evidenceIdsBySide"]["right"]
        decision["sides"] = ["right"]
        decision["evidenceIdsBySide"] = {"right": right_evidence_id}

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review-disposition.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            report = evaluate_review_dispositions(DATASETS, ENRICHMENT_V3, path)

        self.assertEqual(report["summary"]["unassessed"], 1)
        self.assertEqual(
            report["unassessedReviewKeys"],
            [
                {
                    "caseId": "review-porsche-911-partial-variant-label",
                    "side": "left",
                    "evidenceId": "operational:1.0:review-porsche-911-partial-variant-label:left",
                }
            ],
        )
        self.assertNotIn(
            ("review-porsche-911-partial-variant-label", "left"),
            {
                (item["caseId"], item["side"])
                for item in report["durableHumanReviewItems"]
            },
        )

    def test_stale_side_disposition_is_reported(self) -> None:
        payload = json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
        decision = next(
            item
            for item in payload["decisions"]
            if item["caseId"] == "review-ford-mustang-variant-missing"
        )
        right_evidence_id = decision["evidenceIdsBySide"]["right"]
        left_evidence_id = "operational:1.0:review-ford-mustang-variant-missing:left"
        decision["sides"] = ["left", "right"]
        decision["evidenceIdsBySide"] = {
            "left": left_evidence_id,
            "right": right_evidence_id,
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review-disposition.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            report = evaluate_review_dispositions(DATASETS, ENRICHMENT_V3, path)

        self.assertEqual(report["summary"]["unusedDispositions"], 1)
        self.assertEqual(
            report["unusedDispositionKeys"],
            [
                {
                    "caseId": "review-ford-mustang-variant-missing",
                    "side": "left",
                    "evidenceId": left_evidence_id,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
