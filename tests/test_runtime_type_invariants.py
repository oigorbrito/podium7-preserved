from datetime import datetime, timezone
import math
import unittest

from podium7.domain import (
    CandidateFact,
    CanonicalFact,
    Conflict,
    ProvenanceRecord,
    RawEvidence,
    Source,
)


class RuntimeTypeInvariantTests(unittest.TestCase):
    def test_text_fields_reject_non_string_values(self):
        with self.assertRaises(ValueError):
            Source(None, "Example", "https://example.test")
        with self.assertRaises(ValueError):
            CandidateFact(
                id="candidate-1",
                entity_candidate_id="entity-1",
                attribute="power",
                raw_value=1,
                normalized_value=1,
                unit=123,
                evidence_id="evidence-1",
                extraction_method="test",
            )

    def test_raw_evidence_requires_datetime_instance(self):
        with self.assertRaises(ValueError):
            RawEvidence(
                id="evidence-1",
                source_id="source-1",
                locator="https://example.test/evidence",
                retrieved_at="2026-08-19T00:00:00Z",
                acquisition_method="test",
                raw_content_ref="sha256:abc@fixture",
            )

    def test_confidence_requires_finite_non_boolean_probability(self):
        base = {
            "id": "candidate-1",
            "entity_candidate_id": "entity-1",
            "attribute": "power",
            "raw_value": 1,
            "normalized_value": 1,
            "unit": "kW",
            "evidence_id": "evidence-1",
            "extraction_method": "test",
        }
        for confidence in (True, False, "0.5", math.nan, math.inf, -math.inf, -0.1, 1.1):
            with self.subTest(confidence=confidence):
                with self.assertRaises(ValueError):
                    CandidateFact(**base, confidence=confidence)

    def test_canonical_fact_requires_provenance_record_instance(self):
        with self.assertRaises(ValueError):
            CanonicalFact(
                id="canonical-1",
                entity_id="entity-1",
                attribute="power",
                accepted_value=1,
                candidate_references=("candidate-1",),
                fusion_decision="test",
                provenance={"entity_id": "entity-1"},
            )

    def test_conflict_requires_conflict_state_enum(self):
        with self.assertRaises(ValueError):
            Conflict(
                id="conflict-1",
                attribute="power",
                candidate_references=("candidate-1", "candidate-2"),
                reason="test",
                resolution_state="UNRESOLVED",
            )


if __name__ == "__main__":
    unittest.main()
