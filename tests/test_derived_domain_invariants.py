import unittest

from podium7.domain import CandidateFact, CanonicalFact, Conflict, ProvenanceRecord


class DerivedDomainInvariantTests(unittest.TestCase):
    def test_candidate_fact_requires_identifiers_and_non_empty_optional_tokens(self):
        base = {
            "id": "candidate-1",
            "entity_candidate_id": "entity-1",
            "attribute": "power",
            "raw_value": 300,
            "normalized_value": 223.709961,
            "unit": "kW",
            "evidence_id": "evidence-1",
            "extraction_method": "structured-json-v1",
            "normalization_rule": "power.hp_to_kw.v1",
        }
        for field in ("id", "entity_candidate_id", "attribute", "evidence_id", "extraction_method"):
            invalid = dict(base)
            invalid[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    CandidateFact(**invalid)
        for field in ("unit", "normalization_rule"):
            invalid = dict(base)
            invalid[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    CandidateFact(**invalid)

    def test_provenance_requires_identity_activity_and_unique_derivations(self):
        with self.assertRaises(ValueError):
            ProvenanceRecord(entity_id="", activity_id="fusion-1")
        with self.assertRaises(ValueError):
            ProvenanceRecord(entity_id="entity-1", activity_id="")
        with self.assertRaises(ValueError):
            ProvenanceRecord(
                entity_id="entity-1",
                activity_id="fusion-1",
                was_derived_from=("candidate-1", "candidate-1"),
            )
        with self.assertRaises(ValueError):
            ProvenanceRecord(
                entity_id="entity-1",
                activity_id="fusion-1",
                was_derived_from=("",),
            )

    def test_canonical_fact_requires_identifiers_and_unique_candidate_references(self):
        provenance = ProvenanceRecord(
            entity_id="entity-1",
            activity_id="fusion-1",
            was_derived_from=("candidate-1",),
        )
        base = {
            "id": "canonical-1",
            "entity_id": "entity-1",
            "attribute": "power",
            "accepted_value": 223.709961,
            "candidate_references": ("candidate-1",),
            "fusion_decision": "single-candidate.v1",
            "provenance": provenance,
        }
        for field in ("id", "entity_id", "attribute", "fusion_decision"):
            invalid = dict(base)
            invalid[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    CanonicalFact(**invalid)
        duplicate = dict(base)
        duplicate["candidate_references"] = ("candidate-1", "candidate-1")
        with self.assertRaises(ValueError):
            CanonicalFact(**duplicate)

    def test_conflict_requires_identifiers_reason_and_unique_candidate_references(self):
        base = {
            "id": "conflict-1",
            "attribute": "power",
            "candidate_references": ("candidate-1", "candidate-2"),
            "reason": "normalized values disagree",
        }
        for field in ("id", "attribute", "reason"):
            invalid = dict(base)
            invalid[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    Conflict(**invalid)
        duplicate = dict(base)
        duplicate["candidate_references"] = ("candidate-1", "candidate-1")
        with self.assertRaises(ValueError):
            Conflict(**duplicate)


if __name__ == "__main__":
    unittest.main()
