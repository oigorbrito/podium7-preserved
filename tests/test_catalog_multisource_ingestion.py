from __future__ import annotations

from copy import deepcopy
import unittest

from podium7.catalog import CatalogMatchOutcome, CatalogStore, CatalogVehicleIdentity
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.catalog_multisource_ingestion import (
    ingest_catalog_multisource_v2,
    resolve_catalog_multisource_review_create,
    resolve_catalog_multisource_review_match,
)
from podium7.catalog_multisource_review import CatalogMultisourceReviewQueue
from podium7.catalog_multisource_v2 import (
    CATALOG_MULTISOURCE_V2_CONTRACT,
    parse_catalog_multisource_v2_record,
)
from podium7.catalog_review import CatalogReviewResolutionAction, CatalogReviewState


def payload() -> dict[str, object]:
    return {
        "contractVersion": CATALOG_MULTISOURCE_V2_CONTRACT,
        "recordId": "example:corolla-cross:xrx",
        "vehicle": {
            "make": "Toyota",
            "model": "Corolla Cross",
            "generation": "2020 global generation",
            "variant": "XRX Hybrid",
            "powertrain": "1.8 hybrid flex",
            "transmission": "Hybrid Transaxle CVT",
            "body_style": "SUV",
            "market": "BR",
            "model_year_from": 2025,
            "model_year_to": 2025,
        },
        "provenance": {
            "sources": [
                {"id": "source-generation", "name": "Generation source", "locator": "https://example.test/generation"},
                {"id": "source-configuration", "name": "Configuration source", "locator": "https://example.test/configuration"},
            ],
            "evidence": [
                {
                    "id": "evidence-generation",
                    "sourceId": "source-generation",
                    "locator": "https://example.test/generation/corolla-cross",
                    "retrievedAt": "2026-08-31T12:00:00+00:00",
                    "acquisitionMethod": "fixture",
                    "rawContentRef": "fixture:generation",
                },
                {
                    "id": "evidence-configuration",
                    "sourceId": "source-configuration",
                    "locator": "https://example.test/configuration/corolla-cross",
                    "retrievedAt": "2026-08-31T12:00:00+00:00",
                    "acquisitionMethod": "fixture",
                    "rawContentRef": "fixture:configuration",
                },
            ],
            "fieldEvidence": {
                "make": ["evidence-generation", "evidence-configuration"],
                "model": ["evidence-generation", "evidence-configuration"],
                "generation": ["evidence-generation"],
                "variant": ["evidence-configuration"],
                "powertrain": ["evidence-configuration"],
                "transmission": ["evidence-configuration"],
                "body_style": ["evidence-configuration"],
                "market": ["evidence-generation", "evidence-configuration"],
                "model_year_from": ["evidence-configuration"],
                "model_year_to": ["evidence-configuration"],
            },
        },
    }


def expected_identity() -> CatalogVehicleIdentity:
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
    )


def review_payload() -> dict[str, object]:
    value = payload()
    vehicle = value["vehicle"]
    provenance = value["provenance"]
    assert isinstance(vehicle, dict)
    assert isinstance(provenance, dict)
    del vehicle["variant"]
    field_evidence = provenance["fieldEvidence"]
    assert isinstance(field_evidence, dict)
    del field_evidence["variant"]
    return value


class CatalogMultisourceIngestionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CatalogStore()

    def tearDown(self) -> None:
        self.store.close()

    def test_create_persists_complete_identity_and_field_evidence_candidates(self) -> None:
        envelope = parse_catalog_multisource_v2_record(payload())
        result = ingest_catalog_multisource_v2(self.store, envelope)
        self.assertEqual(result.action, CatalogIngestionAction.CREATED)
        self.assertEqual(result.identity, expected_identity())
        self.assertEqual(self.store.get_catalog_vehicle(result.vehicle_id), expected_identity())
        facts = self.store.catalog_candidates_for_entity(result.vehicle_id)
        self.assertEqual(
            {(fact.attribute, fact.evidence_id) for fact in facts},
            {(field, evidence_id) for field, ids in envelope.field_evidence for evidence_id in ids},
        )

    def test_equivalent_input_order_produces_same_semantic_create(self) -> None:
        forward_payload = payload()
        reverse_payload = deepcopy(forward_payload)
        provenance = reverse_payload["provenance"]
        assert isinstance(provenance, dict)
        provenance["sources"] = list(reversed(provenance["sources"]))
        provenance["evidence"] = list(reversed(provenance["evidence"]))
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        for field_name, evidence_ids in tuple(field_evidence.items()):
            field_evidence[field_name] = list(reversed(evidence_ids))
        first_store = CatalogStore()
        second_store = CatalogStore()
        self.addCleanup(first_store.close)
        self.addCleanup(second_store.close)
        first = ingest_catalog_multisource_v2(first_store, parse_catalog_multisource_v2_record(forward_payload))
        second = ingest_catalog_multisource_v2(second_store, parse_catalog_multisource_v2_record(reverse_payload))
        self.assertEqual(first.action, second.action)
        self.assertEqual(first.identity, second.identity)
        self.assertEqual(first.evidence_ids, second.evidence_ids)
        self.assertEqual(
            {(fact.attribute, fact.evidence_id, repr(fact.normalized_value)) for fact in first_store.catalog_candidates_for_entity(first.vehicle_id)},
            {(fact.attribute, fact.evidence_id, repr(fact.normalized_value)) for fact in second_store.catalog_candidates_for_entity(second.vehicle_id)},
        )

    def test_match_attaches_field_evidence_candidates_to_existing_vehicle(self) -> None:
        existing_id = self.store.create_catalog_vehicle(expected_identity())
        envelope = parse_catalog_multisource_v2_record(payload())
        result = ingest_catalog_multisource_v2(self.store, envelope)
        self.assertEqual(result.action, CatalogIngestionAction.MATCHED)
        self.assertEqual(result.vehicle_id, existing_id)
        self.assertEqual(
            {(fact.attribute, fact.evidence_id) for fact in self.store.catalog_candidates_for_entity(existing_id)},
            {(field, evidence_id) for field, ids in envelope.field_evidence for evidence_id in ids},
        )

    def test_one_exact_match_preserves_v1_precedence_over_other_review_candidate(self) -> None:
        exact_id = self.store.create_catalog_vehicle(expected_identity())
        partial_id = self.store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Toyota",
                model="Corolla Cross",
                generation="2020 global generation",
                powertrain="1.8 hybrid flex",
                transmission="Hybrid Transaxle CVT",
                body_style="SUV",
                market="BR",
                model_year_from=2025,
                model_year_to=2025,
            )
        )
        result = ingest_catalog_multisource_v2(self.store, parse_catalog_multisource_v2_record(payload()))
        self.assertEqual(result.action, CatalogIngestionAction.MATCHED)
        self.assertEqual(result.vehicle_id, exact_id)
        outcomes = {item.vehicle_id: item.outcome for item in result.comparisons}
        self.assertEqual(outcomes[exact_id], CatalogMatchOutcome.MATCH)
        self.assertEqual(outcomes[partial_id], CatalogMatchOutcome.REVIEW)

    def test_review_persists_sources_evidence_and_real_field_bindings_without_candidate_facts(self) -> None:
        existing_id = self.store.create_catalog_vehicle(expected_identity())
        envelope = parse_catalog_multisource_v2_record(review_payload())
        result = ingest_catalog_multisource_v2(self.store, envelope)
        self.assertEqual(result.action, CatalogIngestionAction.REVIEW)
        self.assertIsNone(result.vehicle_id)
        self.assertEqual(result.review_vehicle_ids, (existing_id,))
        self.assertIsNotNone(result.review_id)
        self.assertEqual(self.store.catalog_candidates_for_entity(existing_id), [])
        queue = CatalogMultisourceReviewQueue(self.store)
        task = queue.get(result.review_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.state, CatalogReviewState.OPEN)
        self.assertEqual(task.evidence_ids, ("evidence-configuration", "evidence-generation"))
        bindings = queue.review_field_bindings(result.review_id)
        actual = {(item["fieldName"], item["rawEvidenceId"], item["sourceId"]) for item in bindings}
        expected = {
            (field, evidence_id, self.store.get_raw_evidence(evidence_id).source_id)
            for field, ids in envelope.field_evidence
            for evidence_id in ids
        }
        self.assertEqual(actual, expected)

    def test_review_id_is_invariant_to_source_evidence_and_field_reference_order(self) -> None:
        base = review_payload()
        reverse = deepcopy(base)
        provenance = reverse["provenance"]
        assert isinstance(provenance, dict)
        provenance["sources"] = list(reversed(provenance["sources"]))
        provenance["evidence"] = list(reversed(provenance["evidence"]))
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        for field, ids in tuple(field_evidence.items()):
            field_evidence[field] = list(reversed(ids))
        first_store = CatalogStore()
        second_store = CatalogStore()
        self.addCleanup(first_store.close)
        self.addCleanup(second_store.close)
        first_store.create_catalog_vehicle(expected_identity())
        second_store.create_catalog_vehicle(expected_identity())
        first = ingest_catalog_multisource_v2(first_store, parse_catalog_multisource_v2_record(base))
        second = ingest_catalog_multisource_v2(second_store, parse_catalog_multisource_v2_record(reverse))
        self.assertEqual(first.review_id, second.review_id)

    def test_review_match_materializes_all_field_evidence_candidates(self) -> None:
        existing_id = self.store.create_catalog_vehicle(expected_identity())
        envelope = parse_catalog_multisource_v2_record(review_payload())
        result = ingest_catalog_multisource_v2(self.store, envelope)
        task = resolve_catalog_multisource_review_match(
            self.store,
            result.review_id,
            existing_id,
            actor_id="operator-1",
            reason="confirmed existing vehicle",
        )
        self.assertEqual(task.state, CatalogReviewState.RESOLVED)
        self.assertEqual(task.resolution_action, CatalogReviewResolutionAction.MATCHED)
        self.assertEqual(task.resolution_vehicle_id, existing_id)
        self.assertEqual(
            {(fact.attribute, fact.evidence_id) for fact in self.store.catalog_candidates_for_entity(existing_id)},
            {(field, evidence_id) for field, ids in envelope.field_evidence for evidence_id in ids},
        )

    def test_review_create_materializes_all_field_evidence_candidates(self) -> None:
        self.store.create_catalog_vehicle(expected_identity())
        envelope = parse_catalog_multisource_v2_record(review_payload())
        result = ingest_catalog_multisource_v2(self.store, envelope)
        task = resolve_catalog_multisource_review_create(
            self.store,
            result.review_id,
            actor_id="operator-1",
            reason="confirmed new vehicle",
        )
        self.assertEqual(task.state, CatalogReviewState.RESOLVED)
        self.assertEqual(task.resolution_action, CatalogReviewResolutionAction.CREATED)
        self.assertIsNotNone(task.resolution_vehicle_id)
        self.assertEqual(
            {(fact.attribute, fact.evidence_id) for fact in self.store.catalog_candidates_for_entity(task.resolution_vehicle_id)},
            {(field, evidence_id) for field, ids in envelope.field_evidence for evidence_id in ids},
        )


if __name__ == "__main__":
    unittest.main()
