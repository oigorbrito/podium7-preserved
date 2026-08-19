import unittest

from podium7.domain import CandidateFact, ConflictState
from podium7.fusion import fuse_candidates


def candidate(candidate_id, value, unit="kW", attribute="power"):
    return CandidateFact(
        id=candidate_id,
        entity_candidate_id="entity-1",
        attribute=attribute,
        raw_value=value,
        normalized_value=value,
        unit=unit,
        evidence_id=f"evidence-{candidate_id}",
        extraction_method="test",
        normalization_rule="test.rule.v1",
    )


class FusionTests(unittest.TestCase):
    def test_single_candidate_becomes_canonical(self) -> None:
        result = fuse_candidates("entity-1", [candidate("c1", 100)])
        self.assertIsNotNone(result.canonical_fact)
        self.assertIsNone(result.conflict)
        self.assertEqual(result.canonical_fact.accepted_value, {"value": 100, "unit": "kW"})

    def test_agreeing_candidates_become_canonical(self) -> None:
        result = fuse_candidates("entity-1", [candidate("c1", 100), candidate("c2", 100)])
        self.assertIsNotNone(result.canonical_fact)
        self.assertEqual(result.canonical_fact.candidate_references, ("c1", "c2"))

    def test_disagreement_becomes_unresolved_conflict(self) -> None:
        result = fuse_candidates("entity-1", [candidate("c1", 100), candidate("c2", 110)])
        self.assertIsNone(result.canonical_fact)
        self.assertIsNotNone(result.conflict)
        self.assertEqual(result.conflict.resolution_state, ConflictState.UNRESOLVED)

    def test_provenance_contains_all_candidates(self) -> None:
        result = fuse_candidates("entity-1", [candidate("c2", 100), candidate("c1", 100)])
        self.assertEqual(result.canonical_fact.provenance.was_derived_from, ("c1", "c2"))

    def test_mixed_attributes_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fuse_candidates("entity-1", [candidate("c1", 100), candidate("c2", 350, "Nm", "torque")])

    def test_empty_candidate_set_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fuse_candidates("entity-1", [])


if __name__ == "__main__":
    unittest.main()
