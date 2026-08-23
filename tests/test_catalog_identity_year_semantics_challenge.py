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
    / "catalog_identity_year_semantics_challenge_v1.json"
)


class CatalogIdentityYearSemanticsChallengeTests(unittest.TestCase):
    def test_year_semantics_challenge_is_source_backed_and_balanced(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)

        self.assertEqual(dataset.version, "year-semantics-challenge-1.0")
        self.assertEqual(len(dataset.source_ids), 4)
        self.assertEqual(len(dataset.cases), 6)
        self.assertEqual(
            Counter(case.expected for case in dataset.cases),
            Counter(
                {
                    CatalogMatchOutcome.MATCH: 2,
                    CatalogMatchOutcome.NO_MATCH: 2,
                    CatalogMatchOutcome.REVIEW: 2,
                }
            ),
        )
        self.assertTrue(all(case.source_ids for case in dataset.cases))
        self.assertTrue(all(case.rationale.strip() for case in dataset.cases))

    def test_current_resolver_year_semantics_are_characterized(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)
        report = evaluate_catalog_identity_benchmark(dataset)
        metrics = report["metrics"]
        cases = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["totalCases"], 6)
        self.assertEqual(metrics["correct"], 4)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedDuplicateCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 2)
        self.assertEqual(metrics["ambiguousOvercommitRate"], 1.0)
        self.assertEqual(metrics["reviewRate"], 0.0)

        manufacture_conflict = cases[
            "challenge-review-manufacture-year-conflict-same-model-year"
        ]
        self.assertEqual(manufacture_conflict["expected"], "REVIEW")
        self.assertEqual(manufacture_conflict["predicted"], "NO_MATCH")
        self.assertEqual(
            manufacture_conflict["reason"],
            "manufacture_year ranges do not overlap",
        )

        missing_model_year = cases[
            "challenge-review-missing-model-year-across-adjacent-years"
        ]
        self.assertEqual(missing_model_year["expected"], "REVIEW")
        self.assertEqual(missing_model_year["predicted"], "MATCH")
        self.assertEqual(
            missing_model_year["reason"],
            "same model, generation and powertrain without contradiction",
        )


if __name__ == "__main__":
    unittest.main()
