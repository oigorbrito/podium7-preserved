import json
from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.catalog_multisource_ingestion import ingest_catalog_multisource_v2
from podium7.catalog_multisource_v2 import parse_catalog_multisource_v2_record


BENCHMARK = Path("benchmarks/catalog_identity_golden_br_v1.json")
CASE_ID = "br-match-corolla-cross-xrx-hybrid-my25"
SIDE = "left"
GLOBAL_SOURCE = "toyota-corolla-cross-global-launch"
MY25_SOURCE = "toyota-corolla-cross-my25-br"

FIELD_SOURCE_MAP = {
    "make": GLOBAL_SOURCE,
    "model": GLOBAL_SOURCE,
    "generation": GLOBAL_SOURCE,
    "variant": MY25_SOURCE,
    "powertrain": MY25_SOURCE,
    "transmission": MY25_SOURCE,
    "body_style": GLOBAL_SOURCE,
    "market": MY25_SOURCE,
    "model_year_from": MY25_SOURCE,
    "model_year_to": MY25_SOURCE,
}


def _retained_case_and_sources():
    payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    case = next(item for item in payload["cases"] if item["id"] == CASE_ID)
    sources = {item["id"]: item for item in payload["sources"]}
    return payload, case, sources


def _evidence_id(source_id: str) -> str:
    return f"probe:{CASE_ID}:{SIDE}:{source_id}"


def _v2_payload() -> dict[str, object]:
    benchmark, case, sources = _retained_case_and_sources()
    used_source_ids = tuple(sorted(set(FIELD_SOURCE_MAP.values())))
    retrieved_at = f"{benchmark['createdAt']}T00:00:00Z"
    return {
        "contractVersion": "podium7.catalog-operational.v2",
        "recordId": f"probe:{benchmark['datasetVersion']}:{CASE_ID}:{SIDE}",
        "vehicle": case[SIDE],
        "provenance": {
            "sources": [
                {
                    "id": source_id,
                    "name": sources[source_id]["publisher"],
                    "locator": sources[source_id]["url"],
                }
                for source_id in used_source_ids
            ],
            "evidence": [
                {
                    "id": _evidence_id(source_id),
                    "sourceId": source_id,
                    "locator": sources[source_id]["url"],
                    "retrievedAt": retrieved_at,
                    "acquisitionMethod": "retained-composite-probe",
                    "rawContentRef": f"benchmark:{BENCHMARK.name}#{CASE_ID}:{SIDE}:{source_id}",
                }
                for source_id in used_source_ids
            ],
            "fieldEvidence": {
                field_name: [_evidence_id(source_id)]
                for field_name, source_id in FIELD_SOURCE_MAP.items()
            },
        },
    }


class RepresentativeCompositeMultisourceProbeTests(unittest.TestCase):
    def test_retained_source_metadata_supports_candidate_field_partition(self) -> None:
        _, case, sources = _retained_case_and_sources()
        self.assertEqual(case["sourceIds"], [GLOBAL_SOURCE, MY25_SOURCE])
        self.assertIn("2020 global debut", sources[GLOBAL_SOURCE]["supports"])
        self.assertIn("Corolla Cross generation", sources[GLOBAL_SOURCE]["supports"])
        self.assertIn("SUV", sources[GLOBAL_SOURCE]["title"])
        self.assertIn("MY25", sources[MY25_SOURCE]["title"])
        self.assertIn("XRX Hybrid", sources[MY25_SOURCE]["supports"])
        self.assertIn("powertrains and transmissions", sources[MY25_SOURCE]["supports"])

        present_fields = set(case[SIDE])
        self.assertEqual(set(FIELD_SOURCE_MAP), present_fields)
        self.assertEqual(set(FIELD_SOURCE_MAP.values()), set(case["sourceIds"]))
        self.assertEqual(
            set.intersection(*({source_id} for source_id in FIELD_SOURCE_MAP.values())),
            set(),
        )

    def test_retained_composite_side_replays_through_v2_with_reconstructable_provenance(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)
        envelope = parse_catalog_multisource_v2_record(_v2_payload())
        result = ingest_catalog_multisource_v2(store, envelope)

        self.assertEqual(result.action, CatalogIngestionAction.CREATED)
        self.assertEqual(store.get_catalog_vehicle(result.vehicle_id), result.identity)

        facts = store.catalog_candidates_for_entity(result.vehicle_id)
        actual_bindings = {(fact.attribute, fact.evidence_id) for fact in facts}
        expected_bindings = {
            (field_name, _evidence_id(source_id))
            for field_name, source_id in FIELD_SOURCE_MAP.items()
        }
        self.assertEqual(actual_bindings, expected_bindings)

        for field_name, source_id in FIELD_SOURCE_MAP.items():
            evidence = store.get_raw_evidence(_evidence_id(source_id))
            self.assertIsNotNone(evidence, field_name)
            self.assertEqual(evidence.source_id, source_id)
            self.assertIsNotNone(store.get_source(source_id))


if __name__ == "__main__":
    unittest.main()
