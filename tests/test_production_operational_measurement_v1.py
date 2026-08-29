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
        eligibility = measurement["provenanceEligibility"]

        self.assertEqual(eligibility["records"], 60)
        self.assertEqual(
            eligibility["records"],
            eligibility["replayableRecords"] + eligibility["blockedRecords"],
        )
        self.assertGreater(eligibility["replayableRecords"], 0)
        self.assertGreater(eligibility["blockedRecords"], 0)
        self.assertEqual(summary["total"], eligibility["replayableRecords"])
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(
            summary["created"] + summary["matched"] + summary["review"],
            summary["total"],
        )
        self.assertEqual(summary["openReviewTasks"], summary["review"])
        self.assertLessEqual(summary["catalogItems"], summary["total"])
        self.assertAlmostEqual(
            summary["automaticRate"],
            (summary["created"] + summary["matched"]) / summary["total"],
        )
        self.assertAlmostEqual(summary["reviewRate"], summary["review"] / summary["total"])
        self.assertEqual(
            sum(sum(side.values()) for side in measurement["actionsBySide"].values()),
            summary["total"],
        )
        self.assertEqual(sum(measurement["reviewCauses"].values()), summary["review"])
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", measurement["reviewCauses"])

        print("PRODUCTION_OPERATIONAL_MEASUREMENT_V1", measurement)


if __name__ == "__main__":
    unittest.main()
