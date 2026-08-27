import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog_operational import (
    build_source_backed_operational_records,
    measure_source_backed_operational_corpus,
)
from podium7.catalog_quality import evaluate_identity_quality


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


class ProductionQualityMeasurementV2Tests(unittest.TestCase):
    def test_v3_identity_quality_and_operational_load_are_measurable(self) -> None:
        quality = evaluate_identity_quality(DATASETS)
        operational = measure_source_backed_operational_corpus(DATASETS)
        records = build_source_backed_operational_records(DATASETS)

        self.assertEqual(quality["totalCases"], 36)
        self.assertEqual(operational["summary"]["total"], 72)
        self.assertEqual(len(records), 72)

        metrics = quality["metrics"]
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertIsNotNone(metrics["autoMatchPrecision"])
        self.assertIsNotNone(metrics["autoMatchRecall"])
        self.assertGreaterEqual(metrics["autoMatchPrecision"], 0.0)
        self.assertLessEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertGreaterEqual(metrics["autoMatchRecall"], 0.0)
        self.assertLessEqual(metrics["autoMatchRecall"], 1.0)

        summary = operational["summary"]
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(
            summary["created"] + summary["matched"] + summary["review"],
            72,
        )
        self.assertEqual(sum(operational["reviewCauses"].values()), summary["openReviewTasks"])

        self.assertTrue(all(record["source"]["locator"].startswith("https://") for record in records))
        self.assertTrue(all(record["evidence"]["locator"].startswith("https://") for record in records))
        self.assertTrue(all(record["evidence"]["rawContentRef"].startswith("benchmark:") for record in records))

        print(
            "PRODUCTION_QUALITY_MEASUREMENT_V2",
            {"identityQuality": quality["metrics"], "operational": operational},
        )

    def test_ambiguous_overcommit_is_not_double_counted_as_false_merge(self) -> None:
        fixture = {
            "schema": "podium7.catalog-identity-golden.v1",
            "datasetVersion": "metric-separation-v1",
            "sources": [
                {"id": "source-a", "url": "https://example.test/source-a"},
            ],
            "cases": [
                {
                    "id": "ambiguous-overcommit",
                    "expected": "REVIEW",
                    "left": {"make": "Toyota", "model": "Corolla"},
                    "right": {"make": "Toyota", "model": "Corolla"},
                    "sourceIds": ["source-a"],
                    "rationale": "Metric fixture: resolver may overcommit an ambiguous gold case, which is not a false merge by definition.",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            metrics = evaluate_identity_quality((path,))["metrics"]

        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 1)


if __name__ == "__main__":
    unittest.main()
