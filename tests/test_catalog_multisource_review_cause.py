import unittest

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.catalog_multisource_ingestion import ingest_catalog_multisource_v2
from podium7.catalog_multisource_review import CatalogMultisourceReviewQueue
from podium7.catalog_multisource_review_cause import (
    CatalogMultisourceReviewCauseStore,
    snapshot_multisource_review_causes,
)
from podium7.catalog_multisource_v2 import (
    CATALOG_MULTISOURCE_V2_CONTRACT,
    parse_catalog_multisource_v2_record,
)
from podium7.catalog_review_cause import classify_review_causes


def review_payload() -> dict[str, object]:
    return {
        "contractVersion": CATALOG_MULTISOURCE_V2_CONTRACT,
        "recordId": "example:review-causes",
        "vehicle": {
            "make": "Toyota",
            "model": "Corolla Cross",
            "generation": "2020 global generation",
            "powertrain": "1.8 hybrid flex",
            "market": "BR",
        },
        "provenance": {
            "sources": [
                {
                    "id": "source-generation",
                    "name": "Generation source",
                    "locator": "https://example.test/generation",
                },
                {
                    "id": "source-powertrain",
                    "name": "Powertrain source",
                    "locator": "https://example.test/powertrain",
                },
            ],
            "evidence": [
                {
                    "id": "evidence-generation",
                    "sourceId": "source-generation",
                    "locator": "https://example.test/generation/corolla-cross",
                    "retrievedAt": "2026-09-01T12:00:00+00:00",
                    "acquisitionMethod": "fixture",
                    "rawContentRef": "fixture:generation",
                },
                {
                    "id": "evidence-powertrain",
                    "sourceId": "source-powertrain",
                    "locator": "https://example.test/powertrain/corolla-cross",
                    "retrievedAt": "2026-09-01T12:00:00+00:00",
                    "acquisitionMethod": "fixture",
                    "rawContentRef": "fixture:powertrain",
                },
            ],
            "fieldEvidence": {
                "make": ["evidence-generation", "evidence-powertrain"],
                "model": ["evidence-generation", "evidence-powertrain"],
                "generation": ["evidence-generation"],
                "powertrain": ["evidence-powertrain"],
                "market": ["evidence-generation", "evidence-powertrain"],
            },
        },
    }


class CatalogMultisourceReviewCauseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CatalogStore()
        self.existing_id = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Toyota",
                model="Corolla Cross",
                generation="2020 global generation",
                variant="XRX Hybrid",
                powertrain="1.8 hybrid flex",
                market="BR",
            )
        )

    def tearDown(self) -> None:
        self.store.close()

    def test_review_ingestion_snapshots_same_causes_as_existing_classifier(self) -> None:
        result = ingest_catalog_multisource_v2(
            self.store,
            parse_catalog_multisource_v2_record(review_payload()),
        )
        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        self.assertEqual(result.review_vehicle_ids, (self.existing_id,))

        task = CatalogMultisourceReviewQueue(self.store).get(result.review_id)
        self.assertIsNotNone(task)
        snapshot = CatalogMultisourceReviewCauseStore(self.store).get(result.review_id)
        self.assertIsNotNone(snapshot)
        self.assertEqual(
            snapshot.causes,
            classify_review_causes(task.comparisons, task.candidate_vehicle_ids),
        )

    def test_identical_snapshot_is_idempotent(self) -> None:
        result = ingest_catalog_multisource_v2(
            self.store,
            parse_catalog_multisource_v2_record(review_payload()),
        )
        queue = CatalogMultisourceReviewQueue(self.store)
        task = queue.get(result.review_id)
        cause_store = CatalogMultisourceReviewCauseStore(self.store)
        first = cause_store.get(result.review_id)
        second = snapshot_multisource_review_causes(
            self.store,
            review_id=result.review_id,
            comparisons=task.comparisons,
            candidate_vehicle_ids=task.candidate_vehicle_ids,
            cause_store=cause_store,
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
