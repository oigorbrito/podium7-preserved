import json
import unittest

from podium7.domain import AutomotiveIdentity, CanonicalFact, Conflict, EntityKind, ProvenanceRecord
from podium7.export import export_entity_json, export_entity_payload


def sample_identity():
    return AutomotiveIdentity(kind=EntityKind.POWERTRAIN, make="Artega", model="GT", generation="GT (2010)", powertrain="3.6L V6")


def sample_canonical():
    provenance = ProvenanceRecord(entity_id="entity-1", activity_id="fusion-1", was_derived_from=("c1",), was_generated_by="fusion.single_candidate.v1")
    return CanonicalFact(id="fact-1", entity_id="entity-1", attribute="power", accepted_value={"value": 223.7, "unit": "kW"}, candidate_references=("c1",), fusion_decision="single-candidate.v1", provenance=provenance)


class ExportTests(unittest.TestCase):
    def test_payload_contains_entity(self):
        payload = export_entity_payload("entity-1", sample_identity(), [], [])
        self.assertEqual(payload["entity"]["id"], "entity-1")
        self.assertEqual(payload["entity"]["make"], "Artega")

    def test_payload_contains_provenance(self):
        payload = export_entity_payload("entity-1", sample_identity(), [sample_canonical()], [])
        fact = payload["canonicalFacts"][0]
        self.assertEqual(fact["candidate_references"], ["c1"])
        self.assertEqual(fact["provenance"]["was_derived_from"], ["c1"])

    def test_payload_contains_conflict_metadata(self):
        conflict = Conflict(id="conflict-1", attribute="power", candidate_references=("c1", "c2"), reason="disagreement")
        payload = export_entity_payload("entity-1", sample_identity(), [], [conflict])
        self.assertEqual(payload["quality"]["conflictCount"], 1)
        self.assertTrue(payload["quality"]["hasUnresolvedConflicts"])

    def test_json_is_consumable(self):
        decoded = json.loads(export_entity_json("entity-1", sample_identity(), [sample_canonical()], []))
        self.assertEqual(decoded["canonicalFacts"][0]["attribute"], "power")


if __name__ == "__main__":
    unittest.main()
