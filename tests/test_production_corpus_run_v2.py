from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_api import list_catalog_vehicles
from podium7.catalog_operational import (
    build_source_backed_operational_records,
    run_source_backed_operational_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionCorpusRunV2Tests(unittest.TestCase):
    def test_expanded_source_backed_corpus_runs_end_to_end(self) -> None:
        records = build_source_backed_operational_records(DATASETS)
        self.assertEqual(len(records), 12)
        self.assertGreaterEqual(len({record["source"]["id"] for record in records}), 3)
        self.assertTrue(all(record["evidence"]["locator"].startswith("https://") for record in records))

        store = CatalogStore()
        report = run_source_backed_operational_corpus(store, DATASETS)
        self.assertTrue(report.ok)
        self.assertEqual(report.total, 12)
        self.assertEqual(report.failed, 0)
        self.assertEqual(report.created + report.matched + report.review, 12)
        self.assertGreater(report.created, 0)
        self.assertGreater(report.matched, 0)
        self.assertGreater(report.review, 0)

        consumer = list_catalog_vehicles(store, limit=100)
        self.assertTrue(consumer["ok"])
        self.assertGreater(len(consumer["items"]), 0)

        print(
            "PRODUCTION_CORPUS_RUN_V2",
            {
                "total": report.total,
                "created": report.created,
                "matched": report.matched,
                "review": report.review,
                "failed": report.failed,
                "consumerItems": len(consumer["items"]),
            },
        )


if __name__ == "__main__":
    unittest.main()
