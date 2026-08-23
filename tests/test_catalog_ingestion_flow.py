import unittest
from datetime import datetime, timezone

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_ingestion import CatalogIngestionAction, ingest_catalog_record
from podium7.domain import RawEvidence, Source


SOURCE = Source(
    id="test-source",
    name="Test automotive source",
    locator="https://example.test/vehicles",
)


def evidence(number: int) -> RawEvidence:
    return RawEvidence(
        id=f"evidence-{number}",
        source_id=SOURCE.id,
        locator=f"https://example.test/vehicles/{number}",
        retrieved_at=datetime(2026, 8, 22, 12, number, tzinfo=timezone.utc),
        acquisition_method="test-fixture",
        raw_content_ref=f"sha256:test-{number}",
    )


def corolla_cross_record() -> dict[str, object]:
    return {
        "make": "  Toyota  ",
        "model": "Corolla   Cross",
        "generation": "2020 global generation",
        "variant": "XRX Hybrid",
        "powertrain": "1.8 hybrid flex",
        "transmission": "Hybrid Transaxle CVT",
        "body_style": "SUV",
        "market": "BR",
        "model_year_from": 2025,
        "model_year_to": 2025,
    }


class CatalogIngestionFlowTests(unittest.TestCase):
    def test_new_record_creates_catalog_identity_and_links_evidence(self) -> None:
        store = CatalogStore()

        result = ingest_catalog_record(
            store,
            corolla_cross_record(),
            source=SOURCE,
            evidence=evidence(1),
        )

        self.assertEqual(result.action, CatalogIngestionAction.CREATED)
        self.assertIsNotNone(result.vehicle_id)
        self.assertEqual(result.comparisons, ())
        self.assertEqual(store.get_source(SOURCE.id), SOURCE)
        self.assertEqual(store.get_raw_evidence("evidence-1"), evidence(1))
        self.assertEqual(store.get_catalog_vehicle(result.vehicle_id).make, "Toyota")
        self.assertEqual(store.get_catalog_vehicle(result.vehicle_id).model, "Corolla Cross")

        candidates = store.catalog_candidates_for_entity(result.vehicle_id)
        self.assertGreaterEqual(len(candidates), 8)
        self.assertTrue(all(candidate.evidence_id == "evidence-1" for candidate in candidates))
        self.assertIn("model", {candidate.attribute for candidate in candidates})
        self.assertIn("model_year_from", {candidate.attribute for candidate in candidates})

    def test_second_observation_matches_existing_identity_without_duplicate(self) -> None:
        store = CatalogStore()
        first = ingest_catalog_record(
            store,
            corolla_cross_record(),
            source=SOURCE,
            evidence=evidence(1),
        )

        second = ingest_catalog_record(
            store,
            corolla_cross_record(),
            source=SOURCE,
            evidence=evidence(2),
        )

        self.assertEqual(second.action, CatalogIngestionAction.MATCHED)
        self.assertEqual(second.vehicle_id, first.vehicle_id)
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 1)
        observed_evidence = {
            candidate.evidence_id
            for candidate in store.catalog_candidates_for_entity(first.vehicle_id)
        }
        self.assertEqual(observed_evidence, {"evidence-1", "evidence-2"})

    def test_incomplete_overlap_goes_to_review_without_creating_vehicle(self) -> None:
        store = CatalogStore()
        existing_id = store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Toyota",
                model="Corolla Cross",
                generation="2020 global generation",
                variant="XRX Hybrid",
                powertrain="1.8 hybrid flex",
                transmission="Hybrid Transaxle CVT",
                body_style="SUV",
                market="BR",
            )
        )
        incomplete = corolla_cross_record()
        incomplete.pop("variant")

        result = ingest_catalog_record(
            store,
            incomplete,
            source=SOURCE,
            evidence=evidence(3),
        )

        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        self.assertIsNone(result.vehicle_id)
        self.assertEqual(result.review_vehicle_ids, (existing_id,))
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 1)
        self.assertEqual(store.get_raw_evidence("evidence-3"), evidence(3))

    def test_explicitly_distinct_variant_creates_new_identity(self) -> None:
        store = CatalogStore()
        store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Volkswagen",
                model="T-Cross",
                generation="2019 Brazil generation",
                variant="Highline 250 TSI",
                powertrain="250 TSI flex",
                transmission="automatic",
                body_style="SUV",
                market="BR",
            )
        )

        result = ingest_catalog_record(
            store,
            {
                "make": "Volkswagen",
                "model": "T-Cross",
                "generation": "2019 Brazil generation",
                "variant": "Comfortline 200 TSI",
                "powertrain": "200 TSI flex",
                "transmission": "automatic",
                "body_style": "SUV",
                "market": "BR",
            },
            source=SOURCE,
            evidence=evidence(4),
        )

        self.assertEqual(result.action, CatalogIngestionAction.CREATED)
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 2)
        self.assertEqual(result.comparisons[0].outcome.value, "NO_MATCH")

    def test_multiple_deterministic_matches_are_not_resolved_arbitrarily(self) -> None:
        store = CatalogStore()
        identity = CatalogVehicleIdentity(
            make="Ford",
            model="Mustang",
            generation="7th generation",
            variant="Dark Horse",
            powertrain="5.0 V8",
            transmission="manual",
            body_style="coupe",
            market="BR",
        )
        first = store.create_catalog_vehicle(identity)
        second = store.create_catalog_vehicle(identity)

        result = ingest_catalog_record(
            store,
            {
                "make": "Ford",
                "model": "Mustang",
                "generation": "7th generation",
                "variant": "Dark Horse",
                "powertrain": "5.0 V8",
                "transmission": "manual",
                "body_style": "coupe",
                "market": "BR",
            },
            source=SOURCE,
            evidence=evidence(5),
        )

        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        self.assertIsNone(result.vehicle_id)
        self.assertEqual(set(result.review_vehicle_ids), {first, second})
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 2)


if __name__ == "__main__":
    unittest.main()
