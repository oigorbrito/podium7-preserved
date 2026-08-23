import unittest
from collections import Counter
from pathlib import Path

from podium7.catalog import CatalogMatchOutcome
from podium7.catalog_benchmark import (
    evaluate_catalog_identity_benchmark,
    load_catalog_identity_benchmark,
)


DATASET = (
    Path(__file__).resolve().parents[1]
    / "benchmarks"
    / "catalog_identity_br_adjacent_incomplete_v1.json"
)


class CatalogIdentityBrazilAdjacentIncompleteTests(unittest.TestCase):
    def test_hard_case_slice_is_official_source_backed_and_focused(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)

        self.assertEqual(dataset.version, "br-adjacent-incomplete-1.0")
        self.assertEqual(len(dataset.source_ids), 11)
        self.assertEqual(len(dataset.cases), 6)
        self.assertEqual(
            Counter(case.expected for case in dataset.cases),
            Counter(
                {
                    CatalogMatchOutcome.MATCH: 1,
                    CatalogMatchOutcome.NO_MATCH: 2,
                    CatalogMatchOutcome.REVIEW: 3,
                }
            ),
        )
        self.assertTrue(all(case.source_ids for case in dataset.cases))
        self.assertTrue(all(case.rationale.strip() for case in dataset.cases))
        self.assertTrue(
            all(
                case.left.market == "BR" and case.right.market == "BR"
                for case in dataset.cases
            )
        )

    def test_hard_case_slice_matches_selected_conservative_policy(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)
        report = evaluate_catalog_identity_benchmark(dataset)
        metrics = report["metrics"]
        by_id = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["totalCases"], 6)
        self.assertEqual(metrics["correct"], 6)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedDuplicateCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertEqual(metrics["matchPrecision"], 1.0)
        self.assertEqual(metrics["matchRecall"], 1.0)
        self.assertEqual(metrics["reviewRate"], 0.5)

        self.assertEqual(
            by_id["br-hard-no-match-corolla-altis-hybrid-my25-vs-my26"]["reason"],
            "model_year ranges do not overlap",
        )
        self.assertEqual(
            by_id["br-hard-no-match-onix-premier-my26-vs-my27"]["reason"],
            "model_year ranges do not overlap",
        )
        self.assertEqual(
            by_id[
                "br-hard-review-tcross-highline-current-page-missing-transmission-mapping"
            ]["reason"],
            "trim-defining evidence is incomplete",
        )
        self.assertEqual(
            by_id["br-hard-review-tcross-highline-model-year-present-one-side"]["reason"],
            "model_year evidence is incomplete",
        )


if __name__ == "__main__":
    unittest.main()
