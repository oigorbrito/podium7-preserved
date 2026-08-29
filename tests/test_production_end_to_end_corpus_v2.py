from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_api import list_catalog_vehicles
from podium7.catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload


class ProductionEndToEndCorpusV2Tests(unittest.TestCase):
    def _root(self) -> Path:
        return Path(__file__).resolve().parents[1]

    def _manifest(self) -> dict[str, object]:
        return json.loads(
            (self._root() / "benchmarks" / "production_end_to_end_corpus_v2.json").read_text(
                encoding="utf-8"
            )
        )

    def _records(self, manifest: dict[str, object]) -> list[dict[str, object]]:
        base_path = self._root() / str(manifest["baseCorpus"])
        base = json.loads(base_path.read_text(encoding="utf-8"))
        return [*base["records"], *manifest["additionalRecords"]]

    def test_manifest_binds_exact_retained_snapshot_without_year_reinterpretation(self) -> None:
        manifest = self._manifest()
        snapshot = manifest["sourceSnapshot"]
        raw_path = self._root() / snapshot["path"]
        raw = raw_path.read_bytes()

        self.assertEqual(
            snapshot["sha256"],
            hashlib.sha256(raw).hexdigest(),
        )
        self.assertEqual(
            "560e795a8a0a9e97d20b7b201b3537962c7d6824",
            snapshot["gitBlobSha"],
        )
        self.assertIn("acquisition date only", snapshot["timestampBoundary"])
        self.assertIn("must not be represented", snapshot["timestampBoundary"])

        for record in manifest["additionalRecords"]:
            self.assertEqual("vehicle-makes-models", record["source"]["id"])
            self.assertTrue(
                record["evidence"]["rawContentRef"].startswith(
                    f"sha256:{snapshot['sha256']}@"
                )
            )
            self.assertNotIn("manufacture_year_from", record["vehicle"])
            self.assertNotIn("manufacture_year_to", record["vehicle"])
            self.assertNotIn("model_year_from", record["vehicle"])
            self.assertNotIn("model_year_to", record["vehicle"])

    def test_incremental_corpus_runs_through_catalog_product_path(self) -> None:
        manifest = self._manifest()
        records = self._records(manifest)
        expected = manifest["expected"]

        self.assertEqual(len(records), expected["total"])
        self.assertEqual(
            {record["source"]["id"] for record in records},
            {
                "nhtsa-vpic",
                "fueleconomy-gov",
                "eea-co2-cars",
                "inmetro-pbev",
                "vehicle-makes-models",
            },
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

        additional_results = report.results[-2:]
        self.assertEqual(
            [item.action.value for item in additional_results],
            ["CREATED", "CREATED"],
        )
        for envelope in envelopes:
            self.assertEqual(store.get_raw_evidence(envelope.evidence.id), envelope.evidence)

        consumer = list_catalog_vehicles(store, limit=100)
        self.assertTrue(consumer["ok"])
        self.assertEqual(len(consumer["items"]), expected["consumerItems"])

    def test_corpus_remains_explicitly_bounded(self) -> None:
        manifest = self._manifest()
        self.assertEqual(
            manifest["evidenceClass"],
            "BOUNDED_REPOSITORY_RETAINED_OPERATIONAL_CORPUS",
        )
        self.assertIn("production completeness", manifest["nonClaims"])
        self.assertIn("vehicle-makes-models authority promotion", manifest["nonClaims"])


if __name__ == "__main__":
    unittest.main()
