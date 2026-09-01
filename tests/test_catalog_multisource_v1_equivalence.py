from __future__ import annotations

from datetime import datetime, timezone
import unittest

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_ingestion import CatalogIngestionAction, ingest_catalog_record
from podium7.catalog_multisource_ingestion import ingest_catalog_multisource_v2
from podium7.catalog_multisource_v2 import (
    CATALOG_MULTISOURCE_V2_CONTRACT,
    parse_catalog_multisource_v2_record,
)
from podium7.domain import RawEvidence, Source


SOURCE = Source(
    id="equivalence-source",
    name="Equivalence source",
    locator="https://example.test/equivalence",
)
EVIDENCE = RawEvidence(
    id="equivalence-evidence",
    source_id=SOURCE.id,
    locator="https://example.test/equivalence/corolla",
    retrieved_at=datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc),
    acquisition_method="fixture",
    raw_content_ref="fixture:equivalence",
)
RECORD = {
    "make": "Toyota",
    "model": "Corolla",
    "generation": "12th generation",
    "variant": "Altis Hybrid",
    "powertrain": "1.8 hybrid flex",
    "transmission": "Hybrid Transaxle CVT",
    "body_style": "sedan",
    "market": "BR",
    "model_year_from": 2025,
    "model_year_to": 2025,
}
IDENTITY = CatalogVehicleIdentity(**RECORD)


def v2_envelope():
    return parse_catalog_multisource_v2_record(
        {
            "contractVersion": CATALOG_MULTISOURCE_V2_CONTRACT,
            "recordId": "equivalence:corolla:altis-hybrid",
            "vehicle": dict(RECORD),
            "provenance": {
                "sources": [
                    {
                        "id": SOURCE.id,
                        "name": SOURCE.name,
                        "locator": SOURCE.locator,
                    }
                ],
                "evidence": [
                    {
                        "id": EVIDENCE.id,
                        "sourceId": EVIDENCE.source_id,
                        "locator": EVIDENCE.locator,
                        "retrievedAt": EVIDENCE.retrieved_at.isoformat(),
                        "acquisitionMethod": EVIDENCE.acquisition_method,
                        "rawContentRef": EVIDENCE.raw_content_ref,
                    }
                ],
                "fieldEvidence": {
                    field_name: [EVIDENCE.id]
                    for field_name in RECORD
                },
            },
        }
    )


def semantic_facts(store: CatalogStore, vehicle_id: str) -> set[tuple[str, str, str]]:
    return {
        (fact.attribute, fact.evidence_id, repr(fact.normalized_value))
        for fact in store.catalog_candidates_for_entity(vehicle_id)
    }


class CatalogMultisourceV1EquivalenceTests(unittest.TestCase):
    def test_single_source_create_is_semantically_equivalent(self) -> None:
        v1_store = CatalogStore()
        v2_store = CatalogStore()
        self.addCleanup(v1_store.close)
        self.addCleanup(v2_store.close)

        v1 = ingest_catalog_record(
            v1_store,
            RECORD,
            source=SOURCE,
            evidence=EVIDENCE,
        )
        v2 = ingest_catalog_multisource_v2(v2_store, v2_envelope())

        self.assertEqual(v1.action, CatalogIngestionAction.CREATED)
        self.assertEqual(v2.action, v1.action)
        self.assertEqual(v2.identity, v1.identity)
        self.assertEqual(v1_store.get_catalog_vehicle(v1.vehicle_id), IDENTITY)
        self.assertEqual(v2_store.get_catalog_vehicle(v2.vehicle_id), IDENTITY)
        self.assertEqual(semantic_facts(v2_store, v2.vehicle_id), semantic_facts(v1_store, v1.vehicle_id))
        self.assertEqual(v1_store.get_source(SOURCE.id), v2_store.get_source(SOURCE.id))
        self.assertEqual(v1_store.get_raw_evidence(EVIDENCE.id), v2_store.get_raw_evidence(EVIDENCE.id))

    def test_single_source_match_is_semantically_equivalent(self) -> None:
        v1_store = CatalogStore()
        v2_store = CatalogStore()
        self.addCleanup(v1_store.close)
        self.addCleanup(v2_store.close)
        v1_existing = v1_store.create_catalog_vehicle(IDENTITY)
        v2_existing = v2_store.create_catalog_vehicle(IDENTITY)

        v1 = ingest_catalog_record(
            v1_store,
            RECORD,
            source=SOURCE,
            evidence=EVIDENCE,
        )
        v2 = ingest_catalog_multisource_v2(v2_store, v2_envelope())

        self.assertEqual(v1.action, CatalogIngestionAction.MATCHED)
        self.assertEqual(v2.action, v1.action)
        self.assertEqual(v1.vehicle_id, v1_existing)
        self.assertEqual(v2.vehicle_id, v2_existing)
        self.assertEqual(v2.identity, v1.identity)
        self.assertEqual(semantic_facts(v2_store, v2.vehicle_id), semantic_facts(v1_store, v1.vehicle_id))
        self.assertEqual(v1_store.get_source(SOURCE.id), v2_store.get_source(SOURCE.id))
        self.assertEqual(v1_store.get_raw_evidence(EVIDENCE.id), v2_store.get_raw_evidence(EVIDENCE.id))


if __name__ == "__main__":
    unittest.main()
