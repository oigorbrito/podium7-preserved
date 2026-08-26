import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_api import CATALOG_API_MAX_PAGE_SIZE, list_catalog_vehicles
from podium7.catalog_operational import (
    build_source_backed_operational_records,
    run_source_backed_operational_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


class ProductionCorpusRunV3Tests(unittest.TestCase):
    def test_v3_blocks_ambiguous_case_level_source_attribution(self) -> None:
        with self.assertRaisesRegex(ValueError, "ambiguous case-level source attribution"):
            build_source_backed_operational_records(DATASETS)

    def test_single_source_operational_replay_remains_end_to_end(self) -> None:
        fixture = {
            "schema": "podium7.catalog-identity-golden.v1",
            "datasetVersion": "single-source-operational-v1",
            "createdAt": "2026-08-26",
            "sources": [
                {
                    "id": "toyota-source",
                    "publisher": "Toyota",
                    "url": "https://example.test/toyota",
                }
            ],
            "cases": [
                {
                    "id": "single-source-match",
                    "expected": "MATCH",
                    "left": {"make": "Toyota", "model": "Corolla"},
                    "right": {"make": "Toyota", "model": "Corolla"},
                    "sourceIds": ["toyota-source"],
                    "rationale": "Exact single-source replay fixture.",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "single-source.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            records = build_source_backed_operational_records((path,))
            self.assertEqual(len(records), 2)
            self.assertEqual({record["source"]["id"] for record in records}, {"toyota-source"})
            self.assertTrue(all(record["evidence"]["locator"].startswith("https://") for record in records))
            self.assertTrue(all(record["evidence"]["rawContentRef"].startswith("benchmark:") for record in records))

            store = CatalogStore()
            try:
                report = run_source_backed_operational_corpus(store, (path,))
                self.assertTrue(report.ok)
                self.assertEqual(report.total, 2)
                self.assertEqual(report.failed, 0)
                consumer = list_catalog_vehicles(store, limit=CATALOG_API_MAX_PAGE_SIZE)
                self.assertTrue(consumer["ok"])
                self.assertGreater(len(consumer["items"]), 0)
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
