from datetime import datetime, timezone
import unittest

from podium7.domain import (
    AutomotiveIdentity,
    CandidateFact,
    CanonicalFact,
    Conflict,
    EntityKind,
    ProvenanceRecord,
    RawEvidence,
    Source,
)
from podium7.persistence import EvidenceStore


class PersistenceSemanticIntegrityTests(unittest.TestCase):
    def _seed(self, store: EvidenceStore) -> None:
        source = Source("source-1", "Example", "https://example.test/vehicle")
        entity = AutomotiveIdentity(
            kind=EntityKind.POWERTRAIN,
            make="Artega",
            model="GT",
            generation="GT (2010)",
            powertrain="3.6L V6",
        )
        evidence = RawEvidence(
            id="evidence-1",
            source_id=source.id,
            locator=source.locator,
            retrieved_at=datetime(2026, 8, 19, tzinfo=timezone.utc),
            acquisition_method="test",
            raw_content_ref="fixture.json",
        )
        store.save_source(source)
        store.save_entity("entity-1", entity)
        store.save_raw_evidence(evidence)
        store.save_candidate_fact(
            CandidateFact(
                id="power-1",
                entity_candidate_id="entity-1",
                attribute="power",
                raw_value=300,
                normalized_value=223.709961,
                unit="kW",
                evidence_id=evidence.id,
                extraction_method="test",
                normalization_rule="power.hp_to_kw.v1",
            )
        )
        store.save_candidate_fact(
            CandidateFact(
                id="torque-1",
                entity_candidate_id="entity-1",
                attribute="torque",
                raw_value=350,
                normalized_value=350,
                unit="Nm",
                evidence_id=evidence.id,
                extraction_method="test",
                normalization_rule="torque.nm.identity.v1",
            )
        )

    def test_canonical_rejects_candidate_from_other_attribute(self):
        with EvidenceStore() as store:
            self._seed(store)
            fact = CanonicalFact(
                id="canonical-1",
                entity_id="entity-1",
                attribute="power",
                accepted_value=350,
                candidate_references=("torque-1",),
                fusion_decision="invalid-test",
                provenance=ProvenanceRecord(
                    entity_id="entity-1",
                    activity_id="fusion-invalid",
                    was_derived_from=("torque-1",),
                ),
            )
            with self.assertRaises(ValueError):
                store.save_canonical_fact(fact, "provenance-invalid")
            self.assertIsNone(store.get_provenance("provenance-invalid"))
            self.assertEqual(store.snapshot_counts()["canonical_facts"], 0)

    def test_conflict_rejects_mixed_candidate_attributes(self):
        with EvidenceStore() as store:
            self._seed(store)
            conflict = Conflict(
                id="conflict-1",
                attribute="power",
                candidate_references=("power-1", "torque-1"),
                reason="invalid mixed attribute test",
            )
            with self.assertRaises(ValueError):
                store.save_conflict(conflict)
            self.assertEqual(store.snapshot_counts()["conflicts"], 0)


if __name__ == "__main__":
    unittest.main()
