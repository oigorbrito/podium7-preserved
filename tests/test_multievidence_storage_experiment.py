from datetime import datetime, timezone
import unittest

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.domain import CandidateFact, RawEvidence, Source


class MultiEvidenceStorageExperimentTests(unittest.TestCase):
    def _source(self, source_id: str) -> Source:
        return Source(
            id=source_id,
            name=source_id,
            locator=f"https://example.test/{source_id}",
        )

    def _evidence(self, evidence_id: str, source_id: str) -> RawEvidence:
        return RawEvidence(
            id=evidence_id,
            source_id=source_id,
            locator=f"https://example.test/{evidence_id}",
            retrieved_at=datetime(2026, 8, 31, tzinfo=timezone.utc),
            acquisition_method="test-fixture",
            raw_content_ref=f"sha256:{evidence_id}",
        )

    def _persist_composite(self, source_order: tuple[str, str]) -> tuple[dict[str, str], dict[str, str]]:
        store = CatalogStore()
        self.addCleanup(store.close)

        source_a = self._source("source-a")
        source_b = self._source("source-b")
        evidence_a = self._evidence("evidence-a", source_a.id)
        evidence_b = self._evidence("evidence-b", source_b.id)
        sources = {source_a.id: source_a, source_b.id: source_b}
        evidence = {source_a.id: evidence_a, source_b.id: evidence_b}
        observations = {
            source_a.id: {
                "make": "Example",
                "model": "Road",
                "generation": "G1",
            },
            source_b.id: {
                "variant": "Highline",
                "powertrain": "1.5 turbo",
                "transmission": "7-speed automatic",
                "body_style": "suv",
            },
        }
        identity = CatalogVehicleIdentity(
            make="Example",
            model="Road",
            generation="G1",
            variant="Highline",
            powertrain="1.5 turbo",
            transmission="7-speed automatic",
            body_style="suv",
        )

        with store.transaction():
            for source_id in source_order:
                store.save_source(sources[source_id])
                store.save_raw_evidence(evidence[source_id])
            vehicle_id = store.create_catalog_vehicle(identity)
            for source_id in source_order:
                current_evidence = evidence[source_id]
                for attribute, value in observations[source_id].items():
                    store.save_catalog_candidate_fact(
                        CandidateFact(
                            id=f"candidate:{source_id}:{attribute}",
                            entity_candidate_id=vehicle_id,
                            attribute=attribute,
                            raw_value=value,
                            normalized_value=value,
                            unit=None,
                            evidence_id=current_evidence.id,
                            extraction_method="multievidence-storage-experiment",
                            confidence=None,
                            normalization_rule="test-normalization.v1",
                        )
                    )

        candidate_bindings = {
            fact.attribute: fact.evidence_id
            for fact in store.catalog_candidates_for_entity(vehicle_id)
        }
        evidence_bindings = {
            evidence_id: store.get_raw_evidence(evidence_id).source_id
            for evidence_id in ("evidence-a", "evidence-b")
        }
        return candidate_bindings, evidence_bindings

    def test_storage_preserves_field_evidence_bindings_independent_of_insert_order(self) -> None:
        forward = self._persist_composite(("source-a", "source-b"))
        reverse = self._persist_composite(("source-b", "source-a"))

        expected_candidates = {
            "make": "evidence-a",
            "model": "evidence-a",
            "generation": "evidence-a",
            "variant": "evidence-b",
            "powertrain": "evidence-b",
            "transmission": "evidence-b",
            "body_style": "evidence-b",
        }
        expected_evidence = {
            "evidence-a": "source-a",
            "evidence-b": "source-b",
        }
        self.assertEqual(forward, (expected_candidates, expected_evidence))
        self.assertEqual(reverse, forward)

    def test_storage_transaction_rolls_back_partial_multievidence_write(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)
        source = self._source("rollback-source")
        evidence = self._evidence("rollback-evidence", source.id)

        with self.assertRaisesRegex(RuntimeError, "forced rollback"):
            with store.transaction():
                store.save_source(source)
                store.save_raw_evidence(evidence)
                vehicle_id = store.create_catalog_vehicle(
                    CatalogVehicleIdentity(make="Example", model="Rollback")
                )
                store.save_catalog_candidate_fact(
                    CandidateFact(
                        id="rollback-candidate",
                        entity_candidate_id=vehicle_id,
                        attribute="make",
                        raw_value="Example",
                        normalized_value="Example",
                        unit=None,
                        evidence_id=evidence.id,
                        extraction_method="multievidence-storage-experiment",
                        confidence=None,
                        normalization_rule="test-normalization.v1",
                    )
                )
                raise RuntimeError("forced rollback")

        self.assertIsNone(store.get_source(source.id))
        self.assertIsNone(store.get_raw_evidence(evidence.id))
        self.assertEqual(store.catalog_vehicle_ids_page(after_id=None, limit=10), [])


if __name__ == "__main__":
    unittest.main()
