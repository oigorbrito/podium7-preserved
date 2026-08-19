from datetime import datetime, timezone
from pathlib import Path
import tempfile
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


SOURCE = Source("source-1", "Example", "https://example.test/vehicle")
SECOND_SOURCE = Source("source-2", "Second", "https://example.test/vehicle/2")
ENTITY = AutomotiveIdentity(
    kind=EntityKind.POWERTRAIN,
    make="Artega",
    model="GT",
    generation="GT (2010)",
    powertrain="3.6L V6",
    year_from=2010,
    year_to=2012,
    aliases=("Artega GT",),
    engine_identifiers=("V6-3597",),
    external_identifiers=("external-1",),
)
EVIDENCE = RawEvidence(
    id="evidence-1",
    source_id=SOURCE.id,
    locator=SOURCE.locator,
    retrieved_at=datetime(2026, 8, 19, tzinfo=timezone.utc),
    acquisition_method="structured-import",
    raw_content_ref="data/raw/example.json",
)
CANDIDATE = CandidateFact(
    id="candidate-1",
    entity_candidate_id="entity-1",
    attribute="power",
    raw_value=300,
    normalized_value=223.709961,
    unit="kW",
    evidence_id=EVIDENCE.id,
    extraction_method="structured-json-v1",
    confidence=None,
    normalization_rule="power.hp_to_kw.v1",
)


def seed_candidate_path(store: EvidenceStore) -> None:
    store.save_source(SOURCE)
    store.save_entity("entity-1", ENTITY)
    store.save_raw_evidence(EVIDENCE)
    store.save_candidate_fact(CANDIDATE)


def canonical_fact(fact_id: str = "canonical-1") -> CanonicalFact:
    provenance = ProvenanceRecord(
        entity_id="entity-1",
        activity_id="fusion-1",
        was_derived_from=(CANDIDATE.id,),
        was_generated_by="fusion.single_candidate.v1",
    )
    return CanonicalFact(
        id=fact_id,
        entity_id="entity-1",
        attribute="power",
        accepted_value={"value": 223.709961, "unit": "kW"},
        candidate_references=(CANDIDATE.id,),
        fusion_decision="single-candidate.v1",
        provenance=provenance,
    )


class PersistenceTests(unittest.TestCase):
    def test_source_entity_evidence_candidate_round_trip(self):
        with EvidenceStore() as store:
            seed_candidate_path(store)
            self.assertEqual(store.get_source(SOURCE.id), SOURCE)
            self.assertEqual(store.get_entity("entity-1"), ENTITY)
            self.assertEqual(store.get_raw_evidence(EVIDENCE.id), EVIDENCE)
            self.assertEqual(store.get_candidate_fact(CANDIDATE.id), CANDIDATE)

    def test_file_backed_store_survives_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "podium7.sqlite"
            with EvidenceStore(database) as store:
                seed_candidate_path(store)
            with EvidenceStore(database) as reopened:
                self.assertEqual(reopened.get_source(SOURCE.id), SOURCE)
                self.assertEqual(reopened.get_entity("entity-1"), ENTITY)
                self.assertEqual(reopened.get_raw_evidence(EVIDENCE.id), EVIDENCE)
                self.assertEqual(reopened.get_candidate_fact(CANDIDATE.id), CANDIDATE)

    def test_foreign_key_rejects_evidence_without_source(self):
        orphan = RawEvidence(
            id="orphan",
            source_id="missing-source",
            locator="https://example.test/orphan",
            retrieved_at=datetime(2026, 8, 19, tzinfo=timezone.utc),
            acquisition_method="test",
            raw_content_ref="orphan.json",
        )
        with EvidenceStore() as store:
            with self.assertRaises(ValueError):
                store.save_raw_evidence(orphan)

    def test_duplicate_identifier_is_rejected(self):
        with EvidenceStore() as store:
            store.save_source(SOURCE)
            with self.assertRaises(ValueError):
                store.save_source(SOURCE)

    def test_conflict_round_trip(self):
        conflict = Conflict(
            id="conflict-1",
            attribute="power",
            candidate_references=("candidate-1", "candidate-2"),
            reason="normalized values disagree",
        )
        with EvidenceStore() as store:
            store.save_conflict(conflict)
            self.assertEqual(store.get_conflict(conflict.id), conflict)

    def test_canonical_save_preserves_intermediates_and_provenance(self):
        canonical = canonical_fact()
        with EvidenceStore() as store:
            seed_candidate_path(store)
            store.save_canonical_fact(canonical, "provenance-1")
            counts = store.snapshot_counts()
            self.assertEqual(counts["raw_evidence"], 1)
            self.assertEqual(counts["candidate_facts"], 1)
            self.assertEqual(counts["provenance"], 1)
            self.assertEqual(counts["canonical_facts"], 1)

    def test_canonical_fact_and_provenance_round_trip(self):
        canonical = canonical_fact()
        with EvidenceStore() as store:
            seed_candidate_path(store)
            store.save_canonical_fact(canonical, "provenance-1")
            self.assertEqual(store.get_provenance("provenance-1"), canonical.provenance)
            self.assertEqual(store.get_canonical_fact(canonical.id), canonical)
            self.assertEqual(store.canonical_facts_for_entity("entity-1"), [canonical])

    def test_failed_canonical_save_rolls_back_new_provenance(self):
        canonical = canonical_fact()
        with EvidenceStore() as store:
            seed_candidate_path(store)
            store.save_canonical_fact(canonical, "provenance-1")
            with self.assertRaises(ValueError):
                store.save_canonical_fact(canonical, "provenance-2")
            self.assertIsNone(store.get_provenance("provenance-2"))
            counts = store.snapshot_counts()
            self.assertEqual(counts["provenance"], 1)
            self.assertEqual(counts["canonical_facts"], 1)

    def test_transaction_rolls_back_all_writes_on_failure(self):
        with EvidenceStore() as store:
            with self.assertRaises(RuntimeError):
                with store.transaction():
                    store.save_source(SOURCE)
                    raise RuntimeError("abort")
            self.assertIsNone(store.get_source(SOURCE.id))
            self.assertEqual(store.snapshot_counts()["sources"], 0)

    def test_nested_failure_rolls_back_inner_unit_when_caught(self):
        canonical = canonical_fact()
        with EvidenceStore() as store:
            seed_candidate_path(store)
            store.save_canonical_fact(canonical, "provenance-1")
            with store.transaction():
                try:
                    store.save_canonical_fact(canonical, "provenance-2")
                except ValueError:
                    pass
                store.save_source(SECOND_SOURCE)
            self.assertIsNone(store.get_provenance("provenance-2"))
            self.assertEqual(store.get_source(SECOND_SOURCE.id), SECOND_SOURCE)
            counts = store.snapshot_counts()
            self.assertEqual(counts["provenance"], 1)
            self.assertEqual(counts["canonical_facts"], 1)


if __name__ == "__main__":
    unittest.main()
