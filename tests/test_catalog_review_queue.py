import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from podium7.catalog import CatalogStore, CatalogVehicleIdentity, ExternalIdentifier
from podium7.catalog_ingestion import (
    CatalogIngestionAction,
    ingest_catalog_record,
    resolve_catalog_review_create,
    resolve_catalog_review_match,
)
from podium7.catalog_review import (
    CatalogReviewComparison,
    CatalogReviewQueue,
    CatalogReviewResolutionAction,
    CatalogReviewState,
)
from podium7.domain import RawEvidence, Source


SOURCE = Source(
    id="review-source",
    name="Review source",
    locator="https://example.test/review",
)


def evidence(number: int) -> RawEvidence:
    return RawEvidence(
        id=f"review-evidence-{number}",
        source_id=SOURCE.id,
        locator=f"https://example.test/review/{number}",
        retrieved_at=datetime(2026, 8, 22, 12, number, tzinfo=timezone.utc),
        acquisition_method="test-fixture",
        raw_content_ref=f"sha256:review-{number}",
    )


def full_identity() -> CatalogVehicleIdentity:
    return CatalogVehicleIdentity(
        make="Toyota",
        model="Corolla Cross",
        generation="2020 global generation",
        variant="XRX Hybrid",
        powertrain="1.8 hybrid flex",
        transmission="Hybrid Transaxle CVT",
        body_style="SUV",
        market="BR",
        model_year_from=2025,
        model_year_to=2025,
        aliases=("Corolla Cross Hybrid",),
        engine_identifiers=("2ZR-FXE",),
        external_identifiers=(ExternalIdentifier("fipe", "002199-7"),),
    )


def full_record() -> dict[str, object]:
    identity = full_identity()
    return {
        "make": identity.make,
        "model": identity.model,
        "generation": identity.generation,
        "variant": identity.variant,
        "powertrain": identity.powertrain,
        "transmission": identity.transmission,
        "body_style": identity.body_style,
        "market": identity.market,
        "model_year_from": identity.model_year_from,
        "model_year_to": identity.model_year_to,
        "aliases": list(identity.aliases),
        "engine_identifiers": list(identity.engine_identifiers),
        "external_identifiers": [
            {"namespace": item.namespace, "value": item.value}
            for item in identity.external_identifiers
        ],
    }


class CatalogReviewQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CatalogStore()
        self.queue = CatalogReviewQueue(self.store)

    def tearDown(self) -> None:
        self.store.close()

    def add_evidence(self, number: int) -> RawEvidence:
        if self.store.get_source(SOURCE.id) is None:
            self.store.save_source(SOURCE)
        item = evidence(number)
        self.store.save_raw_evidence(item)
        return item

    def seed_candidate(
        self,
        identity: CatalogVehicleIdentity | None = None,
    ) -> str:
        return self.store.create_catalog_vehicle(identity or full_identity())

    def enqueue(
        self,
        number: int = 1,
        *,
        identity: CatalogVehicleIdentity | None = None,
        candidate_ids: tuple[str, ...] | None = None,
        comparisons: tuple[CatalogReviewComparison, ...] | None = None,
        created_at: datetime | None = None,
    ):
        item = self.add_evidence(number)
        candidates = candidate_ids or (self.seed_candidate(),)
        comparison_items = comparisons or tuple(
            CatalogReviewComparison(vehicle_id, "REVIEW", "incomplete evidence")
            for vehicle_id in candidates
        )
        return self.queue.enqueue(
            evidence_id=item.id,
            identity=identity or full_identity(),
            candidate_vehicle_ids=candidates,
            comparisons=comparison_items,
            created_at=created_at,
        )

    def make_ingestion_review(self, number: int = 20):
        existing_id = self.seed_candidate()
        record = full_record()
        record.pop("variant")
        result = ingest_catalog_record(
            self.store,
            record,
            source=SOURCE,
            evidence=evidence(number),
        )
        return existing_id, result

    def test_schema_is_initialized_as_separate_component(self) -> None:
        self.assertEqual(self.queue.schema_version, 1)
        self.assertEqual(self.store.catalog_schema_version, 1)

    def test_enqueue_round_trips_identity(self) -> None:
        task = self.enqueue()
        self.assertEqual(task.identity, full_identity())
        self.assertEqual(task.state, CatalogReviewState.OPEN)

    def test_enqueue_requires_existing_evidence(self) -> None:
        candidate = self.seed_candidate()
        with self.assertRaisesRegex(ValueError, "evidence does not exist"):
            self.queue.enqueue(
                evidence_id="missing",
                identity=full_identity(),
                candidate_vehicle_ids=(candidate,),
                comparisons=(
                    CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
                ),
            )

    def test_enqueue_requires_candidate(self) -> None:
        item = self.add_evidence(2)
        with self.assertRaisesRegex(ValueError, "at least one candidate"):
            self.queue.enqueue(
                evidence_id=item.id,
                identity=full_identity(),
                candidate_vehicle_ids=(),
                comparisons=(
                    CatalogReviewComparison("veh_missing", "REVIEW", "incomplete"),
                ),
            )

    def test_enqueue_rejects_duplicate_candidates(self) -> None:
        item = self.add_evidence(3)
        candidate = self.seed_candidate()
        with self.assertRaisesRegex(ValueError, "must be unique"):
            self.queue.enqueue(
                evidence_id=item.id,
                identity=full_identity(),
                candidate_vehicle_ids=(candidate, candidate),
                comparisons=(
                    CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
                ),
            )

    def test_enqueue_rejects_missing_candidate_vehicle(self) -> None:
        item = self.add_evidence(4)
        with self.assertRaisesRegex(ValueError, "does not exist"):
            self.queue.enqueue(
                evidence_id=item.id,
                identity=full_identity(),
                candidate_vehicle_ids=("veh_missing",),
                comparisons=(
                    CatalogReviewComparison("veh_missing", "REVIEW", "incomplete"),
                ),
            )

    def test_enqueue_requires_candidate_in_comparisons(self) -> None:
        item = self.add_evidence(5)
        candidate = self.seed_candidate()
        other = self.seed_candidate(
            CatalogVehicleIdentity(make="Honda", model="Civic")
        )
        with self.assertRaisesRegex(ValueError, "missing from comparisons"):
            self.queue.enqueue(
                evidence_id=item.id,
                identity=full_identity(),
                candidate_vehicle_ids=(candidate,),
                comparisons=(
                    CatalogReviewComparison(other, "NO_MATCH", "make differs"),
                ),
            )

    def test_enqueue_is_idempotent_for_same_payload(self) -> None:
        item = self.add_evidence(6)
        candidate = self.seed_candidate()
        comparisons = (
            CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
        )
        first = self.queue.enqueue(
            evidence_id=item.id,
            identity=full_identity(),
            candidate_vehicle_ids=(candidate,),
            comparisons=comparisons,
        )
        second = self.queue.enqueue(
            evidence_id=item.id,
            identity=full_identity(),
            candidate_vehicle_ids=(candidate,),
            comparisons=comparisons,
        )
        self.assertEqual(first, second)

    def test_review_enqueue_persists_explicit_field_bindings(self) -> None:
        task = self.enqueue(6)
        bindings = self.queue.review_field_bindings(task.id)

        self.assertTrue(bindings)
        self.assertTrue(all(binding["bindingVersion"] == 1 for binding in bindings))
        self.assertEqual(
            {binding["sourceId"] for binding in bindings},
            {SOURCE.id},
        )
        self.assertEqual(
            {binding["rawEvidenceId"] for binding in bindings},
            {task.evidence_id},
        )
        self.assertIn("make", {binding["fieldName"] for binding in bindings})
        self.assertIn("model", {binding["fieldName"] for binding in bindings})

    def test_enqueue_rejects_same_evidence_with_different_identity(self) -> None:
        task = self.enqueue(7)
        changed = CatalogVehicleIdentity(make="Toyota", model="RAV4")
        with self.assertRaisesRegex(ValueError, "different review task"):
            self.queue.enqueue(
                evidence_id=task.evidence_id,
                identity=changed,
                candidate_vehicle_ids=task.candidate_vehicle_ids,
                comparisons=task.comparisons,
            )

    def test_review_enqueue_rolls_back_bindings_on_failure(self) -> None:
        item = self.add_evidence(7)
        candidate = self.seed_candidate()
        self.store._connection.execute(
            """
            CREATE TRIGGER review_binding_fail AFTER INSERT ON catalog_v2_review_field_bindings
            WHEN NEW.field_name = 'model'
            BEGIN
                SELECT RAISE(ABORT, 'binding failure');
            END
            """
        )
        with self.assertRaisesRegex(ValueError, "binding failure"):
            self.queue.enqueue(
                evidence_id=item.id,
                identity=full_identity(),
                candidate_vehicle_ids=(candidate,),
                comparisons=(
                    CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
                ),
            )
        self.assertIsNone(self.queue.get_by_evidence(item.id))
        self.assertEqual(self.queue.review_field_bindings("review_missing"), [])

    def test_legacy_review_without_binding_remains_explicit(self) -> None:
        item = self.add_evidence(8)
        candidate = self.seed_candidate()
        task = self.queue.enqueue(
            evidence_id=item.id,
            identity=full_identity(),
            candidate_vehicle_ids=(candidate,),
            comparisons=(
                CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
            ),
        )
        self.store._connection.execute(
            "DELETE FROM catalog_v2_review_field_bindings WHERE review_id = ?",
            (task.id,),
        )
        self.assertEqual(self.queue.review_field_bindings(task.id), [])
        self.assertIsNotNone(self.queue.get(task.id))

    def test_get_unknown_returns_none(self) -> None:
        self.assertIsNone(self.queue.get("review_missing"))

    def test_get_by_evidence_returns_task(self) -> None:
        task = self.enqueue(8)
        self.assertEqual(self.queue.get_by_evidence(task.evidence_id), task)

    def test_open_tasks_returns_only_open(self) -> None:
        first = self.enqueue(9)
        second = self.enqueue(10)
        self.queue.resolve(
            first.id,
            action=CatalogReviewResolutionAction.MATCHED,
            vehicle_id=first.candidate_vehicle_ids[0],
            actor_id="reviewer",
            reason="same vehicle",
        )
        self.assertEqual([item.id for item in self.queue.open_tasks()], [second.id])

    def test_open_tasks_orders_oldest_first(self) -> None:
        base = datetime(2026, 8, 22, tzinfo=timezone.utc)
        later = self.enqueue(11, created_at=base + timedelta(minutes=2))
        earlier = self.enqueue(12, created_at=base)
        self.assertEqual(
            [item.id for item in self.queue.open_tasks()],
            [earlier.id, later.id],
        )

    def test_open_tasks_rejects_zero_limit(self) -> None:
        with self.assertRaises(ValueError):
            self.queue.open_tasks(limit=0)

    def test_open_tasks_rejects_boolean_limit(self) -> None:
        with self.assertRaises(ValueError):
            self.queue.open_tasks(limit=True)

    def test_open_tasks_honors_limit(self) -> None:
        self.enqueue(13)
        self.enqueue(14)
        self.assertEqual(len(self.queue.open_tasks(limit=1)), 1)

    def test_review_persists_after_database_reopen(self) -> None:
        handle = tempfile.NamedTemporaryFile(delete=False)
        path = handle.name
        handle.close()
        try:
            self.store.close()
            first_store = CatalogStore(path)
            first_queue = CatalogReviewQueue(first_store)
            first_store.save_source(SOURCE)
            first_store.save_raw_evidence(evidence(15))
            candidate = first_store.create_catalog_vehicle(full_identity())
            task = first_queue.enqueue(
                evidence_id=evidence(15).id,
                identity=full_identity(),
                candidate_vehicle_ids=(candidate,),
                comparisons=(
                    CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
                ),
            )
            first_store.close()

            second_store = CatalogStore(path)
            second_queue = CatalogReviewQueue(second_store)
            restored = second_queue.get(task.id)
            second_store.close()
            self.assertEqual(restored, task)
        finally:
            if os.path.exists(path):
                os.remove(path)
            self.store = CatalogStore()
            self.queue = CatalogReviewQueue(self.store)

    def test_external_identifiers_round_trip(self) -> None:
        task = self.enqueue(16)
        self.assertEqual(
            task.identity.external_identifiers,
            (ExternalIdentifier("fipe", "002199-7"),),
        )

    def test_comparisons_round_trip(self) -> None:
        item = self.add_evidence(17)
        candidate = self.seed_candidate()
        other = self.seed_candidate(CatalogVehicleIdentity(make="Ford", model="Focus"))
        comparisons = (
            CatalogReviewComparison(candidate, "REVIEW", "trim incomplete"),
            CatalogReviewComparison(other, "NO_MATCH", "make differs"),
        )
        task = self.queue.enqueue(
            evidence_id=item.id,
            identity=full_identity(),
            candidate_vehicle_ids=(candidate,),
            comparisons=comparisons,
        )
        self.assertEqual(task.comparisons, comparisons)

    def test_ingestion_review_creates_durable_task(self) -> None:
        existing, result = self.make_ingestion_review(18)
        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        self.assertIsNotNone(result.review_id)
        task = self.queue.get(result.review_id)
        self.assertEqual(task.candidate_vehicle_ids, (existing,))
        self.assertEqual(task.evidence_id, evidence(18).id)

    def test_ingestion_multiple_matches_creates_durable_task(self) -> None:
        first = self.seed_candidate()
        second = self.seed_candidate()
        result = ingest_catalog_record(
            self.store,
            full_record(),
            source=SOURCE,
            evidence=evidence(19),
        )
        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        self.assertEqual(set(result.review_vehicle_ids), {first, second})
        self.assertIsNotNone(self.queue.get(result.review_id))

    def test_ingestion_created_has_no_review_task(self) -> None:
        result = ingest_catalog_record(
            self.store,
            full_record(),
            source=SOURCE,
            evidence=evidence(20),
        )
        self.assertEqual(result.action, CatalogIngestionAction.CREATED)
        self.assertIsNone(result.review_id)
        self.assertEqual(self.queue.count_open(), 0)

    def test_ingestion_matched_has_no_review_task(self) -> None:
        self.seed_candidate()
        result = ingest_catalog_record(
            self.store,
            full_record(),
            source=SOURCE,
            evidence=evidence(21),
        )
        self.assertEqual(result.action, CatalogIngestionAction.MATCHED)
        self.assertIsNone(result.review_id)
        self.assertEqual(self.queue.count_open(), 0)

    def test_ingestion_review_reuses_task_for_same_evidence(self) -> None:
        self.seed_candidate()
        record = full_record()
        record.pop("variant")
        first = ingest_catalog_record(
            self.store,
            record,
            source=SOURCE,
            evidence=evidence(22),
        )
        second = ingest_catalog_record(
            self.store,
            record,
            source=SOURCE,
            evidence=evidence(22),
        )
        self.assertEqual(first.review_id, second.review_id)
        self.assertEqual(self.queue.count_open(), 1)

    def test_resolve_match_marks_task_resolved(self) -> None:
        existing, result = self.make_ingestion_review(23)
        task = resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="source omitted trim",
        )
        self.assertEqual(task.state, CatalogReviewState.RESOLVED)
        self.assertEqual(task.resolution_action, CatalogReviewResolutionAction.MATCHED)
        self.assertEqual(task.resolution_vehicle_id, existing)

    def test_resolve_match_attaches_observations(self) -> None:
        existing, result = self.make_ingestion_review(24)
        resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same configuration",
        )
        facts = self.store.catalog_candidates_for_entity(existing)
        self.assertTrue(facts)
        self.assertEqual({fact.evidence_id for fact in facts}, {evidence(24).id})

    def test_resolve_match_requires_candidate(self) -> None:
        _, result = self.make_ingestion_review(25)
        unrelated = self.seed_candidate(CatalogVehicleIdentity(make="Honda", model="Civic"))
        with self.assertRaisesRegex(ValueError, "not a candidate"):
            resolve_catalog_review_match(
                self.store,
                result.review_id,
                unrelated,
                actor_id="alice",
                reason="wrong selection",
            )

    def test_resolve_match_accepts_candidate_redirect(self) -> None:
        existing, result = self.make_ingestion_review(26)
        survivor = self.seed_candidate(full_identity())
        self.store.merge_catalog_vehicle_ids(survivor, existing)
        task = resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="candidate was merged",
        )
        self.assertEqual(task.resolution_vehicle_id, survivor)

    def test_resolve_match_requires_actor(self) -> None:
        existing, result = self.make_ingestion_review(27)
        with self.assertRaisesRegex(ValueError, "actor_id"):
            resolve_catalog_review_match(
                self.store,
                result.review_id,
                existing,
                actor_id="",
                reason="same",
            )

    def test_resolve_match_requires_reason(self) -> None:
        existing, result = self.make_ingestion_review(28)
        with self.assertRaisesRegex(ValueError, "reason"):
            resolve_catalog_review_match(
                self.store,
                result.review_id,
                existing,
                actor_id="alice",
                reason="",
            )

    def test_resolve_match_is_idempotent_for_same_resolution(self) -> None:
        existing, result = self.make_ingestion_review(29)
        first = resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        second = resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        self.assertEqual(first, second)

    def test_resolve_match_rejects_conflicting_second_resolution(self) -> None:
        existing, result = self.make_ingestion_review(30)
        resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        with self.assertRaisesRegex(ValueError, "already resolved"):
            resolve_catalog_review_create(
                self.store,
                result.review_id,
                actor_id="alice",
                reason="create instead",
            )

    def test_resolve_create_creates_vehicle(self) -> None:
        _, result = self.make_ingestion_review(31)
        before = len(self.store.catalog_vehicle_ids_page(limit=100))
        task = resolve_catalog_review_create(
            self.store,
            result.review_id,
            actor_id="bob",
            reason="distinct configuration after review",
        )
        after = len(self.store.catalog_vehicle_ids_page(limit=100))
        self.assertEqual(after, before + 1)
        self.assertIsNotNone(self.store.get_catalog_vehicle(task.resolution_vehicle_id))

    def test_resolve_create_attaches_observations(self) -> None:
        _, result = self.make_ingestion_review(32)
        task = resolve_catalog_review_create(
            self.store,
            result.review_id,
            actor_id="bob",
            reason="distinct",
        )
        facts = self.store.catalog_candidates_for_entity(task.resolution_vehicle_id)
        self.assertTrue(facts)
        self.assertEqual({fact.evidence_id for fact in facts}, {evidence(32).id})

    def test_resolve_create_records_resolution_metadata(self) -> None:
        _, result = self.make_ingestion_review(33)
        task = resolve_catalog_review_create(
            self.store,
            result.review_id,
            actor_id="bob",
            reason="distinct",
        )
        self.assertEqual(task.resolution_action, CatalogReviewResolutionAction.CREATED)
        self.assertEqual(task.resolved_by, "bob")
        self.assertEqual(task.resolution_reason, "distinct")
        self.assertIsNotNone(task.resolved_at)

    def test_resolve_create_requires_actor(self) -> None:
        _, result = self.make_ingestion_review(34)
        with self.assertRaisesRegex(ValueError, "actor_id"):
            resolve_catalog_review_create(
                self.store,
                result.review_id,
                actor_id="",
                reason="distinct",
            )

    def test_resolve_create_requires_reason(self) -> None:
        _, result = self.make_ingestion_review(35)
        with self.assertRaisesRegex(ValueError, "reason"):
            resolve_catalog_review_create(
                self.store,
                result.review_id,
                actor_id="bob",
                reason="",
            )

    def test_resolve_create_is_idempotent_for_same_resolution(self) -> None:
        _, result = self.make_ingestion_review(36)
        first = resolve_catalog_review_create(
            self.store,
            result.review_id,
            actor_id="bob",
            reason="distinct",
        )
        count = len(self.store.catalog_vehicle_ids_page(limit=100))
        second = resolve_catalog_review_create(
            self.store,
            result.review_id,
            actor_id="bob",
            reason="distinct",
        )
        self.assertEqual(first, second)
        self.assertEqual(len(self.store.catalog_vehicle_ids_page(limit=100)), count)

    def test_resolved_task_is_removed_from_open_queue(self) -> None:
        existing, result = self.make_ingestion_review(37)
        resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        self.assertNotIn(result.review_id, {task.id for task in self.queue.open_tasks()})

    def test_open_count_tracks_resolutions(self) -> None:
        existing, result = self.make_ingestion_review(38)
        self.assertEqual(self.queue.count_open(), 1)
        resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        self.assertEqual(self.queue.count_open(), 0)

    def test_resolve_unknown_review_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not exist"):
            resolve_catalog_review_create(
                self.store,
                "review_missing",
                actor_id="bob",
                reason="distinct",
            )

    def test_created_resolution_identity_matches_review_identity(self) -> None:
        _, result = self.make_ingestion_review(39)
        task = resolve_catalog_review_create(
            self.store,
            result.review_id,
            actor_id="bob",
            reason="distinct",
        )
        self.assertEqual(
            self.store.get_catalog_vehicle(task.resolution_vehicle_id),
            task.identity,
        )

    def test_enqueue_rejects_same_evidence_with_changed_candidates(self) -> None:
        task = self.enqueue(40)
        other = self.seed_candidate(CatalogVehicleIdentity(make="Honda", model="Civic"))
        with self.assertRaisesRegex(ValueError, "different review task"):
            self.queue.enqueue(
                evidence_id=task.evidence_id,
                identity=task.identity,
                candidate_vehicle_ids=(other,),
                comparisons=(
                    CatalogReviewComparison(other, "REVIEW", "new candidate"),
                ),
            )

    def test_resolution_timestamp_is_timezone_aware(self) -> None:
        existing, result = self.make_ingestion_review(41)
        task = resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        self.assertIsNotNone(task.resolved_at.utcoffset())

    def test_ingestion_payload_exposes_review_id(self) -> None:
        _, result = self.make_ingestion_review(42)
        payload = result.to_payload()
        self.assertEqual(payload["reviewId"], result.review_id)
        self.assertIsNone(payload["vehicleId"])

    def test_task_payload_exposes_resolution_fields(self) -> None:
        existing, result = self.make_ingestion_review(43)
        task = resolve_catalog_review_match(
            self.store,
            result.review_id,
            existing,
            actor_id="alice",
            reason="same",
        )
        payload = task.to_payload()
        self.assertEqual(payload["state"], "RESOLVED")
        self.assertEqual(payload["resolutionAction"], "MATCHED")
        self.assertEqual(payload["resolutionVehicleId"], existing)

    def test_review_comparison_rejects_unknown_outcome(self) -> None:
        with self.assertRaisesRegex(ValueError, "outcome"):
            CatalogReviewComparison("veh_1", "MAYBE", "unknown")

    def test_review_comparison_requires_reason(self) -> None:
        with self.assertRaisesRegex(ValueError, "reason"):
            CatalogReviewComparison("veh_1", "REVIEW", "")

    def test_queue_resolve_rejects_naive_timestamp(self) -> None:
        task = self.enqueue(44)
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.queue.resolve(
                task.id,
                action=CatalogReviewResolutionAction.MATCHED,
                vehicle_id=task.candidate_vehicle_ids[0],
                actor_id="alice",
                reason="same",
                resolved_at=datetime(2026, 8, 22),
            )

    def test_queue_enqueue_rejects_naive_timestamp(self) -> None:
        item = self.add_evidence(45)
        candidate = self.seed_candidate()
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.queue.enqueue(
                evidence_id=item.id,
                identity=full_identity(),
                candidate_vehicle_ids=(candidate,),
                comparisons=(
                    CatalogReviewComparison(candidate, "REVIEW", "incomplete"),
                ),
                created_at=datetime(2026, 8, 22),
            )


if __name__ == "__main__":
    unittest.main()
