from pathlib import Path
import unittest

from podium7.catalog_coverage import (
    MEASURED_FIELDS,
    measure_published_catalog_identity_coverage,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class CatalogIdentityFieldCoverageTests(unittest.TestCase):
    def test_measurement_runs_after_real_consumer_projection(self) -> None:
        report = measure_published_catalog_identity_coverage(DATASETS)

        self.assertTrue(report["operational"]["ok"])
        self.assertEqual(report["operational"]["total"], 60)
        self.assertEqual(report["operational"]["failed"], 0)
        self.assertGreater(report["publishedVehicles"], 0)
        self.assertEqual(set(report["fields"]), set(MEASURED_FIELDS))

        for field in MEASURED_FIELDS:
            field_report = report["fields"][field]
            self.assertEqual(
                field_report["present"] + field_report["missing"],
                report["publishedVehicles"],
            )
            self.assertGreaterEqual(field_report["coverage"], 0.0)
            self.assertLessEqual(field_report["coverage"], 1.0)
            self.assertLessEqual(
                field_report["normalizedDistinct"], field_report["rawDistinct"]
            )

        print("CATALOG_IDENTITY_FIELD_COVERAGE", report)


if __name__ == "__main__":
    unittest.main()
