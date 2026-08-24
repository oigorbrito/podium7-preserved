from pathlib import Path
import unittest

from podium7.catalog_quality import evaluate_identity_quality


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionIdentityQualityV1Tests(unittest.TestCase):
    def test_source_backed_identity_gold_has_zero_unsafe_overcommit(self) -> None:
        report = evaluate_identity_quality(DATASETS)
        metrics = report["metrics"]

        self.assertEqual(report["totalCases"], 30)
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedMatchCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertGreater(metrics["reviewRate"], 0.0)
        self.assertLess(metrics["reviewRate"], 1.0)

    def test_empty_quality_input_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one identity benchmark"):
            evaluate_identity_quality(())


if __name__ == "__main__":
    unittest.main()
