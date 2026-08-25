import unittest
from collections import Counter
from pathlib import Path

from podium7.catalog import CatalogMatchOutcome, resolve_catalog_pair
from podium7.catalog_benchmark import (
    evaluate_catalog_identity_benchmark,
    load_catalog_identity_benchmark,
)
from podium7.catalog_resolution_precedence import (
    resolve_catalog_pair_with_structural_precedence,
)


DATASET = (
    Path(__file__).resolve().parents[1]
    / "benchmarks"
    / "catalog_identity_year_semantics_challenge_v1.json"
)


class CatalogIdentityYearSemanticsChallengeTests(unittest.TestCase):
    def test_year_semantics_regression_is_source_backed(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)

        self.assertEqual(dataset.version, "year-semantics-1.1")
        self.assertEqual(len(dataset.source_ids), 4)
        self.assertEqual(len(dataset.cases), 6)
        self.assertEqual(
            Counter(case.expected for case in dataset.cases),
            Counter(
                {
                    CatalogMatchOutcome.MATCH: 2,
                    CatalogMatchOutcome.NO_MATCH: 3,
                    CatalogMatchOutcome.REVIEW: 1,
                }
            ),
        )
        self.assertTrue(all(case.source_ids for case in dataset.cases))
        self.assertTrue(all(case.rationale.strip() for case in dataset.cases))

    def test_selected_year_semantics_are_exact_regression(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)
        report = evaluate_catalog_identity_benchmark(dataset)
        metrics = report["metrics"]
        cases = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["totalCases"], 6)
        self.assertEqual(metrics["correct"], 6)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedDuplicateCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertEqual(metrics["matchPrecision"], 1.0)
        self.assertEqual(metrics["matchRecall"], 1.0)
        self.assertEqual(metrics["reviewRate"], 1 / 6)

        manufacture_conflict = cases[
            "regression-no-match-manufacture-year-conflict-same-model-year"
        ]
        self.assertEqual(manufacture_conflict["expected"], "NO_MATCH")
        self.assertEqual(manufacture_conflict["predicted"], "NO_MATCH")
        self.assertEqual(
            manufacture_conflict["reason"],
            "manufacture_year ranges do not overlap",
        )

        missing_model_year = cases[
            "regression-review-missing-model-year-across-adjacent-years"
        ]
        self.assertEqual(missing_model_year["expected"], "REVIEW")
        self.assertEqual(missing_model_year["predicted"], "REVIEW")
        self.assertEqual(
            missing_model_year["reason"],
            "model_year evidence is incomplete",
        )

    def test_operational_precedence_path_preserves_selected_year_semantics(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)

        for case in dataset.cases:
            with self.subTest(case=case.id):
                canonical = resolve_catalog_pair(case.left, case.right)
                operational = resolve_catalog_pair_with_structural_precedence(
                    case.left,
                    case.right,
                )
                self.assertEqual(operational, canonical)
                self.assertIs(operational.outcome, case.expected)


if __name__ == "__main__":
    unittest.main()
