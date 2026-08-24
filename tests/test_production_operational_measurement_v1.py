from pathlib import Path
import unittest

from podium7.catalog_operational import measure_source_backed_operational_corpus


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionOperationalMeasurementV1Tests(unittest.TestCase):
    def test_measured_replay_is_failure_free_and_review_load_is_visible(self) -> None:
        measurement = measure_source_backed_operational_corpus(DATASETS)
        summary = measurement["summary"]

        self.assertEqual(summary["total"], 60)
        self.assertEqual(summary["created"], 19)
        self.assertEqual(summary["matched"], 19)
        self.assertEqual(summary["review"], 22)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["catalogItems"], 19)
        self.assertEqual(summary["openReviewTasks"], 22)
        self.assertAlmostEqual(summary["automaticRate"], 38 / 60)
        self.assertAlmostEqual(summary["reviewRate"], 22 / 60)
        self.assertEqual(sum(measurement["actionsBySide"]["left"].values()), 30)
        self.assertEqual(sum(measurement["actionsBySide"]["right"].values()), 30)
        self.assertEqual(sum(measurement["reviewCauses"].values()), 22)
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", measurement["reviewCauses"])

        print("PRODUCTION_OPERATIONAL_MEASUREMENT_V1", measurement)


if __name__ == "__main__":
    unittest.main()
