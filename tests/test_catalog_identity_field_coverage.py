from pathlib import Path
import unittest

from podium7.catalog_coverage import (
    BRAZIL_MARKET,
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
        self.assertEqual(set(report["byDataset"]), {path.name for path in DATASETS})
        self.assertIsInstance(report["contractVersion"], str)
        self.assertTrue(report["contractVersion"])
        self.assertEqual(report["knowledgeState"]["unknown"], "JSON null")
        self.assertEqual(report["brazil"]["market"], BRAZIL_MARKET)
        self.assertGreater(report["brazil"]["total"], 0)
        self.assertEqual(
            report["reviewEvidence"]["count"],
            report["operational"]["review"],
        )
        self.assertFalse(report["reviewEvidence"]["fieldAttributionAvailable"])

        dataset_identities = report["datasets"]
        self.assertEqual(
            {item["name"] for item in dataset_identities},
            {path.name for path in DATASETS},
        )
        for identity in dataset_identities:
            self.assertTrue(identity["schema"])
            self.assertTrue(identity["datasetVersion"])
            self.assertEqual(len(identity["sha256"]), 64)

        for field in MEASURED_FIELDS:
            field_report = report["fields"][field]
            self.assertEqual(
                field_report["present"] + field_report["unknownNull"],
                report["publishedVehicles"],
            )
            self.assertGreaterEqual(field_report["coverage"], 0.0)
            self.assertLessEqual(field_report["coverage"], 1.0)
            self.assertLessEqual(
                field_report["normalizedDistinct"], field_report["rawDistinct"]
            )

        for dataset_name, dataset_report in report["byDataset"].items():
            self.assertTrue(dataset_report["operational"]["ok"])
            self.assertEqual(dataset_report["operational"]["failed"], 0)
            self.assertEqual(dataset_report["dataset"]["name"], dataset_name)
            self.assertEqual(len(dataset_report["dataset"]["sha256"]), 64)
            for field in MEASURED_FIELDS:
                field_report = dataset_report["fields"][field]
                self.assertEqual(
                    field_report["present"] + field_report["unknownNull"],
                    dataset_report["total"],
                )

        print("CATALOG_IDENTITY_FIELD_COVERAGE", report)


if __name__ == "__main__":
    unittest.main()
