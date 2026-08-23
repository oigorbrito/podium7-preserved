from datetime import datetime, timezone
import unittest

from podium7.domain import (
    AutomotiveIdentity,
    CandidateFact,
    EntityKind,
    RawEvidence,
    Source,
)
from podium7.fusion import fuse_candidates
from podium7.persistence import EvidenceStore


class BoundedValuePersistenceTests(unittest.TestCase):
    def test_bounded_curb_weight_round_trips_through_candidate_and_canonical_storage(self) -> None:
        source = Source("source-range", "Range source", "https://example.test/range")
        evidence = RawEvidence(
            id="evidence-range",
            source_id=source.id,
            locator=source.locator,
            retrieved_at=datetime(2026, 8, 23, tzinfo=timezone.utc),
            acquisition_method="web-artifact-v2",
            raw_content_ref="data/raw/range.txt",
        )
        entity = AutomotiveIdentity(
            kind=EntityKind.VARIANT,
            make="Toyota",
            model="Corolla Cross",
            variant="2.0 AWD",
        )
        bounded = {"minValue": 1490, "maxValue": 1508}
        candidate = CandidateFact(
            id="candidate-range",
            entity_candidate_id="entity-range",
            attribute="curb_weight",
            raw_value="3285 - 3325 lbs (1490 - 1508 kg)",
            normalized_value=bounded,
            unit="kg",
            evidence_id=evidence.id,
            extraction_method="autoevolution.curb_weight.bounded.v2",
            normalization_rule="curb_weight.bounded_to_kg.v1",
        )

        with EvidenceStore() as store:
            store.save_source(source)
            store.save_entity("entity-range", entity)
            store.save_raw_evidence(evidence)
            store.save_candidate_fact(candidate)
            self.assertEqual(store.get_candidate_fact(candidate.id), candidate)

            fused = fuse_candidates("entity-range", [candidate])
            self.assertIsNotNone(fused.canonical_fact)
            self.assertIsNone(fused.conflict)
            canonical = fused.canonical_fact
            assert canonical is not None
            self.assertEqual(
                canonical.accepted_value,
                {"value": bounded, "unit": "kg"},
            )
            store.save_canonical_fact(canonical, "provenance-range")
            self.assertEqual(store.get_canonical_fact(canonical.id), canonical)


if __name__ == "__main__":
    unittest.main()
