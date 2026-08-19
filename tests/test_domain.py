from datetime import datetime, timezone
import unittest

from podium7.domain import (
    AutomotiveIdentity,
    CandidateFact,
    CanonicalFact,
    Conflict,
    ConflictState,
    EntityKind,
    ProvenanceRecord,
    RawEvidence,
    Source,
)


class DomainModelTests(unittest.TestCase):
    def test_source_and_raw_evidence_preserve_origin(self) -> None:
        source = Source("src-1", "Example Source", "https://example.test/vehicle/1")
        evidence = RawEvidence(
            id="ev-1",
            source_id=source.id,
            locator=source.locator,
            retrieved_at=datetime(2026, 8, 19, tzinfo=timezone.utc),
            acquisition_method="structured-import",
            raw_content_ref="sha256:abc",
        )
        self.assertEqual(evidence.source_id, source.id)
        self.assertEqual(evidence.locator, source.locator)

    def test_automotive_identity_rejects_invalid_year_range(self) -> None:
        with self.assertRaises(ValueError):
            AutomotiveIdentity(
                kind=EntityKind.GENERATION,
                make="Example",
                model="Model",
                year_from=2025,
                year_to=2024,
            )

    def test_candidate_fact_preserves_raw_and_normalized_values(self) -> None:
        fact = CandidateFact(
            id="cf-1",
            entity_candidate_id="entity-1",
            attribute="power",
            raw_value="110 kW",
            normalized_value=110,
            unit="kW",
            evidence_id="ev-1",
            extraction_method="structured-import",
            confidence=0.95,
            normalization_rule="power.kw.identity.v1",
        )
        self.assertEqual(fact.raw_value, "110 kW")
        self.assertEqual(fact.normalized_value, 110)
        self.assertEqual(fact.normalization_rule, "power.kw.identity.v1")

    def test_canonical_fact_requires_candidate_reference_and_provenance(self) -> None:
        provenance = ProvenanceRecord(
            entity_id="canonical-1",
            activity_id="fusion-1",
            was_derived_from=("cf-1",),
            was_generated_by="fusion-1",
        )
        canonical = CanonicalFact(
            id="fact-1",
            entity_id="canonical-1",
            attribute="power",
            accepted_value=110,
            candidate_references=("cf-1",),
            fusion_decision="single-supported-candidate",
            provenance=provenance,
        )
        self.assertEqual(canonical.provenance.was_derived_from, ("cf-1",))

    def test_canonical_fact_rejects_missing_candidate_derivation(self) -> None:
        provenance = ProvenanceRecord(
            entity_id="canonical-1",
            activity_id="fusion-1",
            was_derived_from=("cf-1",),
        )
        with self.assertRaises(ValueError):
            CanonicalFact(
                id="fact-1",
                entity_id="canonical-1",
                attribute="power",
                accepted_value=110,
                candidate_references=("cf-1", "cf-2"),
                fusion_decision="invalid-provenance-test",
                provenance=provenance,
            )

    def test_canonical_fact_rejects_provenance_for_other_entity(self) -> None:
        provenance = ProvenanceRecord(
            entity_id="other-entity",
            activity_id="fusion-1",
            was_derived_from=("cf-1",),
        )
        with self.assertRaises(ValueError):
            CanonicalFact(
                id="fact-1",
                entity_id="canonical-1",
                attribute="power",
                accepted_value=110,
                candidate_references=("cf-1",),
                fusion_decision="invalid-provenance-entity-test",
                provenance=provenance,
            )

    def test_conflict_preserves_multiple_candidates(self) -> None:
        conflict = Conflict(
            id="conflict-1",
            attribute="power",
            candidate_references=("cf-1", "cf-2"),
            reason="normalized values disagree",
        )
        self.assertEqual(conflict.resolution_state, ConflictState.UNRESOLVED)
        self.assertEqual(len(conflict.candidate_references), 2)

    def test_resolved_conflict_requires_valid_selected_candidate(self) -> None:
        with self.assertRaises(ValueError):
            Conflict(
                id="conflict-2",
                attribute="power",
                candidate_references=("cf-1", "cf-2"),
                reason="normalized values disagree",
                resolution_state=ConflictState.RESOLVED,
            )

        with self.assertRaises(ValueError):
            Conflict(
                id="conflict-3",
                attribute="power",
                candidate_references=("cf-1", "cf-2"),
                reason="normalized values disagree",
                selected_candidate_id="cf-3",
            )


if __name__ == "__main__":
    unittest.main()
