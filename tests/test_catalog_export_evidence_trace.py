import unittest
from datetime import datetime, timezone

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_api import list_catalog_vehicles, lookup_catalog_vehicle
from podium7.domain import CandidateFact, RawEvidence, Source


class CatalogExportEvidenceTraceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CatalogStore()
        self.source = Source(
            id="trace-source",
            name="Trace Source",
            locator="https://example.test/source",
        )
        self.evidence = RawEvidence(
            id="trace-evidence",
            source_id=self.source.id,
            locator="https://example.test/evidence",
            retrieved_at=datetime(2026, 8, 26, tzinfo=timezone.utc),
            acquisition_method="test-fixture",
            raw_content_ref="sha256:trace-evidence",
        )
        self.store.save_source(self.source)
        self.store.save_raw_evidence(self.evidence)
        self.vehicle_id = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", market="BR")
        )
        self.store.save_catalog_candidate_fact(
            CandidateFact(
                id="candidate-model",
                entity_candidate_id=self.vehicle_id,
                attribute="model",
                raw_value="Corolla",
                normalized_value="Corolla",
                unit=None,
                evidence_id=self.evidence.id,
                extraction_method="test-extraction",
                confidence=None,
                normalization_rule="test-normalization.v1",
            )
        )
        self.store.save_catalog_candidate_fact(
            CandidateFact(
                id="candidate-make",
                entity_candidate_id=self.vehicle_id,
                attribute="make",
                raw_value="Toyota",
                normalized_value="Toyota",
                unit=None,
                evidence_id=self.evidence.id,
                extraction_method="test-extraction",
                confidence=None,
                normalization_rule="test-normalization.v1",
            )
        )

    def tearDown(self) -> None:
        self.store.close()

    def test_lookup_exposes_deterministic_persisted_evidence_trace(self) -> None:
        response = lookup_catalog_vehicle(self.store, self.vehicle_id)
        self.assertTrue(response["ok"])
        trace = response["vehicle"]["evidenceTrace"]
        self.assertEqual(
            [entry["candidateFactId"] for entry in trace],
            ["candidate-make", "candidate-model"],
        )
        self.assertEqual(trace[0]["evidenceId"], self.evidence.id)
        self.assertEqual(trace[0]["sourceId"], self.source.id)
        self.assertEqual(trace[0]["evidenceLocator"], self.evidence.locator)
        self.assertEqual(trace[0]["sourceLocator"], self.source.locator)
        self.assertEqual(trace[0]["rawContentRef"], self.evidence.raw_content_ref)
        self.assertEqual(trace[0]["extractionMethod"], "test-extraction")
        self.assertEqual(trace[0]["normalizationRule"], "test-normalization.v1")
        self.assertNotIn("rawValue", trace[0])
        self.assertNotIn("normalizedValue", trace[0])

    def test_list_exposes_same_trace(self) -> None:
        lookup = lookup_catalog_vehicle(self.store, self.vehicle_id)
        listed = list_catalog_vehicles(self.store, limit=10)
        self.assertTrue(listed["ok"])
        self.assertEqual(len(listed["items"]), 1)
        self.assertEqual(
            listed["items"][0]["evidenceTrace"],
            lookup["vehicle"]["evidenceTrace"],
        )

    def test_redirect_resolves_to_canonical_trace(self) -> None:
        duplicate = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", market="BR")
        )
        canonical = self.store.merge_catalog_vehicle_ids(self.vehicle_id, duplicate)
        response = lookup_catalog_vehicle(self.store, duplicate)
        self.assertTrue(response["ok"])
        self.assertTrue(response["redirected"])
        self.assertEqual(response["canonicalId"], canonical)
        self.assertEqual(response["vehicle"]["entity"]["id"], canonical)
        self.assertEqual(len(response["vehicle"]["evidenceTrace"]), 2)

    def test_missing_evidence_fails_closed(self) -> None:
        self.store._connection.execute("PRAGMA foreign_keys = OFF")
        self.store._connection.execute(
            "DELETE FROM raw_evidence WHERE id = ?",
            (self.evidence.id,),
        )
        self.store._connection.commit()
        with self.assertRaisesRegex(ValueError, "missing evidence"):
            lookup_catalog_vehicle(self.store, self.vehicle_id)

    def test_missing_source_fails_closed(self) -> None:
        self.store._connection.execute("PRAGMA foreign_keys = OFF")
        self.store._connection.execute(
            "DELETE FROM sources WHERE id = ?",
            (self.source.id,),
        )
        self.store._connection.commit()
        with self.assertRaisesRegex(ValueError, "missing source"):
            list_catalog_vehicles(self.store, limit=10)


if __name__ == "__main__":
    unittest.main()
