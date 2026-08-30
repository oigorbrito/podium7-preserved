from dataclasses import dataclass
import math
import unittest

from podium7.domain import CandidateFact, CanonicalFact, ProvenanceRecord
from podium7.export import export_entity_json


@dataclass(frozen=True)
class UnsafeIdentityPayload:
    kind: str = "Model"
    make: str = "Example"
    model: str = "Model"
    year_from: float = math.nan


class StrictJsonTests(unittest.TestCase):
    def base_candidate(self):
        return {
            "id": "candidate-1",
            "entity_candidate_id": "entity-1",
            "attribute": "custom_metric",
            "raw_value": 1,
            "normalized_value": 1,
            "unit": None,
            "evidence_id": "evidence-1",
            "extraction_method": "test",
        }

    def test_candidate_fact_rejects_non_standard_json_values(self):
        base = self.base_candidate()
        for field, value in (
            ("raw_value", math.nan),
            ("normalized_value", math.inf),
            ("raw_value", {"not", "json"}),
            ("raw_value", (1, 2)),
            ("normalized_value", {1: "coerced-key"}),
        ):
            invalid = dict(base)
            invalid[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    CandidateFact(**invalid)

    def test_candidate_fact_accepts_identity_preserving_nested_json(self):
        base = self.base_candidate()
        value = {
            "range": [1, 2.5, None],
            "flags": {"verified": True, "label": "ok"},
        }
        base["raw_value"] = value
        base["normalized_value"] = value
        fact = CandidateFact(**base)
        self.assertEqual(value, fact.raw_value)
        self.assertEqual(value, fact.normalized_value)

    def test_canonical_fact_rejects_non_standard_json_accepted_value(self):
        provenance = ProvenanceRecord(
            entity_id="entity-1",
            activity_id="fusion-1",
            was_derived_from=("candidate-1",),
        )
        with self.assertRaises(ValueError):
            CanonicalFact(
                id="canonical-1",
                entity_id="entity-1",
                attribute="custom_metric",
                accepted_value={"value": -math.inf},
                candidate_references=("candidate-1",),
                fusion_decision="test",
                provenance=provenance,
            )

    def test_export_rejects_non_finite_payload_values(self):
        with self.assertRaises(ValueError):
            export_entity_json("entity-1", UnsafeIdentityPayload(), [], [])


if __name__ == "__main__":
    unittest.main()
