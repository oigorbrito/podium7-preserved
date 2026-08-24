from __future__ import annotations

import json
from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_api import list_catalog_vehicles
from podium7.catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload


class ProductionEndToEndCorpusV1Tests(unittest.TestCase):
    def _benchmark(self) -> dict[str, object]:
        path = Path(__file__).resolve().parents[1] / "benchmarks" / "production_end_to_end_corpus_v1.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_bounded_official_source_corpus_runs_through_catalog_product_path(self) -> None:
        benchmark = self._benchmark()
        records = benchmark["records"]
        expected = benchmark["expected"]
        self.assertEqual(
            {record["source"]["id"] for record in records},
            {"nhtsa-vpic", "fueleconomy-gov", "eea-co2-cars", "inmetro-pbev"},
        )

        store = CatalogStore()
        envelopes = parse_catalog_batch_payload({"records": records})
        report = ingest_catalog_batch(store, envelopes)

        self.assertTrue(report.ok)
        self.assertEqual(report.total, expected["total"])
        self.assertEqual(report.created, expected["created"])
        self.assertEqual(report.matched, expected["matched"])
        self.assertEqual(report.review, expected["review"])
        self.assertEqual(report.failed, expected["failed"])
        self.assertEqual(
            len(store.catalog_vehicle_ids_page(limit=100)),
            expected["catalogVehicles"],
        )
        self.assertEqual(
            [item.action.value for item in report.results],
            ["CREATED", "MATCHED", "CREATED", "MATCHED", "CREATED", "REVIEW"],
        )
        self.assertIsNotNone(report.results[-1].review_id)

        for envelope in envelopes:
            self.assertEqual(store.get_raw_evidence(envelope.evidence.id), envelope.evidence)

        consumer = list_catalog_vehicles(store, limit=100)
        self.assertTrue(consumer["ok"])
        self.assertEqual(len(consumer["items"]), expected["consumerItems"])
        for item in consumer["items"]:
            self.assertEqual(item["contractVersion"], "2.0")
            self.assertTrue(item["entity"]["id"])
            self.assertTrue(item["entity"]["make"])
            self.assertTrue(item["entity"]["model"])
            self.assertIsInstance(item["redirectsFrom"], list)

    def test_corpus_explicitly_does_not_claim_production_completeness(self) -> None:
        benchmark = self._benchmark()
        self.assertEqual(benchmark["evidenceClass"], "LOCALLY_VERIFIED_OPERATIONAL_CORPUS")
        self.assertIn("without claiming production completeness", benchmark["description"])


if __name__ == "__main__":
    unittest.main()
