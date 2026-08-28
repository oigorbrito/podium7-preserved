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

        self.assertEqual(summary["total"], 12)
        self.assertEqual(summary["created"], 4)
        self.assertEqual(summary["matched"], 4)
        self.assertEqual(summary["review"], 4)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["catalogItems"], 4)
        self.assertEqual(summary["openReviewTasks"], 4)
        self.assertAlmostEqual(summary["automaticRate"], 8 / 12)
        self.assertAlmostEqual(summary["reviewRate"], 4 / 12)
        self.assertEqual(sum(measurement["actionsBySide"]["left"].values()), 6)
        self.assertEqual(sum(measurement["actionsBySide"]["right"].values()), 6)
        self.assertEqual(sum(measurement["reviewCauses"].values()), 4)
        self.assertEqual(measurement["reviewCauses"], {
            "LABEL_AMBIGUITY": 1,
            "MISSING_IDENTITY_EVIDENCE": 3,
        })
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", measurement["reviewCauses"])

        print("PRODUCTION_OPERATIONAL_MEASUREMENT_V1", measurement)


if __name__ == "__main__":
    unittest.main()
