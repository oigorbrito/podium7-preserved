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
    / "catalog_identity_golden_v1.json"
)


class CatalogIdentityBenchmarkTests(unittest.TestCase):
    def test_golden_v1_is_balanced_and_source_backed(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)

        self.assertEqual(dataset.version, "1.0")
        self.assertEqual(len(dataset.source_ids), 7)
        self.assertEqual(len(dataset.cases), 12)
        self.assertEqual(
            Counter(case.expected for case in dataset.cases),
            Counter(
                {
                    CatalogMatchOutcome.MATCH: 4,
                    CatalogMatchOutcome.NO_MATCH: 4,
                    CatalogMatchOutcome.REVIEW: 4,
                }
            ),
        )
        self.assertTrue(all(case.source_ids for case in dataset.cases))
        self.assertTrue(all(case.rationale.strip() for case in dataset.cases))

    def test_golden_v1_baseline_has_no_false_merge_or_overcommit(self) -> None:
        dataset = load_catalog_identity_benchmark(DATASET)
        report = evaluate_catalog_identity_benchmark(dataset)
        metrics = report["metrics"]

        self.assertEqual(report["totalCases"], 12)
        self.assertEqual(metrics["correct"], 12)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedDuplicateCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertEqual(metrics["matchPrecision"], 1.0)
        self.assertEqual(metrics["matchRecall"], 1.0)
        self.assertEqual(metrics["reviewRate"], 1 / 3)


if __name__ == "__main__":
    unittest.main()
