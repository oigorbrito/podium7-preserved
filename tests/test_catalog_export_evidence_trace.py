import unittest
from datetime import datetime, timezone

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_api import list_catalog_vehicles, lookup_catalog_vehicle
from podium7.catalog_export_trace import (
    TRACE_BUNDLE_SCHEMA,
    export_catalog_vehicle_evidence_bundle,
)
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

    def test_standard_catalog_v2_lookup_and_list_remain_wire_compatible(self) -> None:
        lookup = lookup_catalog_vehicle(self.store, self.vehicle_id)
        listed = list_catalog_vehicles(self.store, limit=10)
        self.assertTrue(lookup["ok"])
        self.assertTrue(listed["ok"])
        self.assertEqual(
            {"contractVersion", "entity", "redirectsFrom"},
            set(lookup["vehicle"]),
        )
        self.assertEqual(
            {"contractVersion", "entity", "redirectsFrom"},
            set(listed["items"][0]),
        )
        self.assertNotIn("evidenceTrace", lookup["vehicle"])
        self.assertNotIn("evidenceTrace", listed["items"][0])

    def test_opt_in_bundle_exposes_deterministic_persisted_evidence_trace(self) -> None:
        bundle = export_catalog_vehicle_evidence_bundle(
            self.store,
            self.vehicle_id,
            contract_version="2.0",
        )
        self.assertEqual(TRACE_BUNDLE_SCHEMA, bundle["schema"])
        self.assertEqual(
            {"contractVersion", "entity", "redirectsFrom"},
            set(bundle["vehicle"]),
        )
        trace = bundle["evidenceTrace"]
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

    def test_redirect_bundle_resolves_to_canonical_trace(self) -> None:
        duplicate = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", market="BR")
        )
        canonical = self.store.merge_catalog_vehicle_ids(self.vehicle_id, duplicate)
        bundle = export_catalog_vehicle_evidence_bundle(
            self.store,
            duplicate,
            contract_version="2.0",
        )
        self.assertEqual(bundle["vehicle"]["entity"]["id"], canonical)
        self.assertEqual(len(bundle["evidenceTrace"]), 2)

    def test_vehicle_without_candidate_evidence_only_blocks_trace_bundle(self) -> None:
        unproven = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Honda", model="Civic", market="BR")
        )
        standard = lookup_catalog_vehicle(self.store, unproven)
        self.assertTrue(standard["ok"])
        with self.assertRaisesRegex(ValueError, "no persisted candidate evidence"):
            export_catalog_vehicle_evidence_bundle(
                self.store,
                unproven,
                contract_version="2.0",
            )

    def test_missing_evidence_fails_closed_in_trace_bundle_without_breaking_v2_shape(self) -> None:
        self.store._connection.execute("PRAGMA foreign_keys = OFF")
        self.store._connection.execute(
            "DELETE FROM raw_evidence WHERE id = ?",
            (self.evidence.id,),
        )
        self.store._connection.commit()
        standard = lookup_catalog_vehicle(self.store, self.vehicle_id)
        self.assertTrue(standard["ok"])
        with self.assertRaisesRegex(ValueError, "missing evidence"):
            export_catalog_vehicle_evidence_bundle(
                self.store,
                self.vehicle_id,
                contract_version="2.0",
            )

    def test_missing_source_fails_closed_in_trace_bundle(self) -> None:
        self.store._connection.execute("PRAGMA foreign_keys = OFF")
        self.store._connection.execute(
            "DELETE FROM sources WHERE id = ?",
            (self.source.id,),
        )
        self.store._connection.commit()
        with self.assertRaisesRegex(ValueError, "missing source"):
            export_catalog_vehicle_evidence_bundle(
                self.store,
                self.vehicle_id,
                contract_version="2.0",
            )


if __name__ == "__main__":
    unittest.main()
