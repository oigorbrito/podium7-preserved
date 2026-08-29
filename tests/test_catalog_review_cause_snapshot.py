import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_ingestion import CatalogIngestionAction, ingest_catalog_record
from podium7.catalog_review import CatalogReviewComparison, CatalogReviewQueue
from podium7.catalog_review_cause import (
    CatalogReviewCauseSnapshot,
    CatalogReviewCauseStore,
    LEGACY_UNSNAPSHOTTED_CAUSE,
    REVIEW_CAUSE_CLASSIFIER_VERSION,
    classify_review_causes,
)
from podium7.domain import RawEvidence, Source


SOURCE = Source("cause-source", "Cause source", "https://example.test/cause")


def evidence(number: int) -> RawEvidence:
    return RawEvidence(
        id=f"cause-evidence-{number}",
        source_id=SOURCE.id,
        locator=f"https://example.test/cause/{number}",
        retrieved_at=datetime(2026, 8, 25, 21, 0, tzinfo=timezone.utc) + timedelta(minutes=number),
        acquisition_method="test-fixture",
        raw_content_ref=f"sha256:cause-{number}",
    )


class CatalogReviewCauseSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CatalogStore()
        self.queue = CatalogReviewQueue(self.store)
        self.store.save_source(SOURCE)

    def tearDown(self) -> None:
        self.store.close()

    def _seed_legacy_review(self, number: int = 1):
        item = evidence(number)
        self.store.save_raw_evidence(item)
        vehicle_id = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", variant=f"XEi-{number}")
        )
        return self.queue.enqueue(
            evidence_id=item.id,
            identity=CatalogVehicleIdentity(make="Toyota", model="Corolla"),
            candidate_vehicle_ids=(vehicle_id,),
            comparisons=(
                CatalogReviewComparison(vehicle_id, "REVIEW", "trim-defining evidence is incomplete"),
            ),
        )

    def test_ingestion_persists_versioned_cause_snapshot(self) -> None:
        self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", variant="XEi")
        )
        result = ingest_catalog_record(
            self.store,
            {"make": "Toyota", "model": "Corolla"},
            source=SOURCE,
            evidence=evidence(2),
        )
        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        snapshot = CatalogReviewCauseStore(self.store).get(result.review_id)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.classifier_version, REVIEW_CAUSE_CLASSIFIER_VERSION)
        self.assertEqual(snapshot.causes, ("MISSING_IDENTITY_EVIDENCE",))

    def test_legacy_review_is_not_retroactively_classified(self) -> None:
        task = self._seed_legacy_review(3)
        self.assertIsNone(CatalogReviewCauseStore(self.store).get(task.id))
        self.assertEqual(LEGACY_UNSNAPSHOTTED_CAUSE, "UNSNAPSHOTTED_LEGACY_REVIEW")

    def test_multiple_causes_are_preserved_without_collapsing(self) -> None:
        comparisons = (
            CatalogReviewComparison("veh_1", "REVIEW", "model labels partially overlap"),
            CatalogReviewComparison("veh_2", "REVIEW", "trim-defining evidence is incomplete"),
        )
        self.assertEqual(
            classify_review_causes(comparisons, ("veh_1", "veh_2")),
            ("LABEL_AMBIGUITY", "MISSING_IDENTITY_EVIDENCE"),
        )

    def test_snapshot_is_idempotent_only_for_identical_content(self) -> None:
        task = self._seed_legacy_review(4)
        cause_store = CatalogReviewCauseStore(self.store)
        snapshot = CatalogReviewCauseSnapshot(
            task.id,
            REVIEW_CAUSE_CLASSIFIER_VERSION,
            ("MISSING_IDENTITY_EVIDENCE",),
        )
        self.assertEqual(cause_store.save(snapshot), cause_store.save(snapshot))
        with self.assertRaisesRegex(ValueError, "different content"):
            cause_store.save(
                CatalogReviewCauseSnapshot(
                    task.id,
                    "catalog-review-cause.v2",
                    ("LABEL_AMBIGUITY",),
                )
            )

    def test_snapshot_persists_across_database_reopen(self) -> None:
        handle = tempfile.NamedTemporaryFile(delete=False)
        path = handle.name
        handle.close()
        try:
            self.store.close()
            first_store = CatalogStore(path)
            first_queue = CatalogReviewQueue(first_store)
            first_store.save_source(SOURCE)
            first_store.save_raw_evidence(evidence(5))
            vehicle_id = first_store.create_catalog_vehicle(
                CatalogVehicleIdentity(make="Toyota", model="Corolla", variant="XEi")
            )
            task = first_queue.enqueue(
                evidence_id=evidence(5).id,
                identity=CatalogVehicleIdentity(make="Toyota", model="Corolla"),
                candidate_vehicle_ids=(vehicle_id,),
                comparisons=(
                    CatalogReviewComparison(vehicle_id, "REVIEW", "model labels partially overlap"),
                ),
            )
            expected = CatalogReviewCauseSnapshot(
                task.id,
                REVIEW_CAUSE_CLASSIFIER_VERSION,
                ("LABEL_AMBIGUITY",),
            )
            CatalogReviewCauseStore(first_store).save(expected)
            first_store.close()

            second_store = CatalogStore(path)
            CatalogReviewQueue(second_store)
            restored = CatalogReviewCauseStore(second_store).get(task.id)
            second_store.close()
            self.assertEqual(restored, expected)
        finally:
            if os.path.exists(path):
                os.remove(path)
            self.store = CatalogStore()
            self.queue = CatalogReviewQueue(self.store)
            self.store.save_source(SOURCE)


if __name__ == "__main__":
    unittest.main()
