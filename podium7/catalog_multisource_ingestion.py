from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .catalog import (
    CatalogMatchOutcome,
    CatalogPublicationAction,
    CatalogStore,
    CatalogVehicleIdentity,
    validate_catalog_publication_change,
)
from .catalog_ingestion import (
    CATALOG_INGESTION_EXTRACTION_METHOD,
    CATALOG_INGESTION_NORMALIZATION_RULE,
    CatalogIngestionAction,
    CatalogIngestionComparison,
    _candidate_id,
    _catalog_entries,
    catalog_identity_from_record,
)
from .catalog_multisource_review import (
    CatalogMultisourceReviewQueue,
    CatalogMultisourceReviewTask,
)
from .catalog_multisource_v2 import CatalogMultisourceV2Envelope
from .catalog_resolution_precedence import resolve_catalog_pair_with_structural_precedence
from .catalog_review import CatalogReviewComparison, CatalogReviewResolutionAction, CatalogReviewState
from .domain import CandidateFact, DecisionStatus, RawEvidence, Source


class CatalogMultisourceIngestionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CatalogMultisourceIngestionResult:
    action: CatalogIngestionAction
    identity: CatalogVehicleIdentity
    evidence_ids: tuple[str, ...]
    vehicle_id: str | None
    comparisons: tuple[CatalogIngestionComparison, ...]
    review_vehicle_ids: tuple[str, ...] = ()
    review_id: str | None = None


def _ensure_source(store: CatalogStore, source: Source) -> None:
    existing = store.get_source(source.id)
    if existing is None:
        store.save_source(source)
    elif existing != source:
        raise ValueError(
            f"source id {source.id!r} already exists with different metadata"
        )


def _ensure_evidence(store: CatalogStore, evidence: RawEvidence) -> None:
    if store.get_source(evidence.source_id) is None:
        raise ValueError(
            f"evidence source does not exist: {evidence.source_id!r}"
        )
    existing = store.get_raw_evidence(evidence.id)
    if existing is None:
        store.save_raw_evidence(evidence)
    elif existing != evidence:
        raise ValueError(
            f"evidence id {evidence.id!r} already exists with different metadata"
        )


def _field_value(identity: CatalogVehicleIdentity, field_name: str) -> Any:
    value = getattr(identity, field_name)
    if field_name in {"aliases", "engine_identifiers"}:
        return list(value)
    if field_name == "external_identifiers":
        return [
            {"namespace": item.namespace, "value": item.value}
            for item in value
        ]
    return value


def _save_field_evidence_candidates(
    store: CatalogStore,
    vehicle_id: str,
    identity: CatalogVehicleIdentity,
    field_evidence: tuple[tuple[str, tuple[str, ...]], ...],
) -> None:
    existing = {
        fact.id: fact for fact in store.catalog_candidates_for_entity(vehicle_id)
    }
    for attribute, evidence_ids in field_evidence:
        value = _field_value(identity, attribute)
        for evidence_id in evidence_ids:
            fact_id = _candidate_id(evidence_id, vehicle_id, attribute)
            fact = CandidateFact(
                id=fact_id,
                entity_candidate_id=vehicle_id,
                attribute=attribute,
                raw_value=value,
                normalized_value=value,
                unit=None,
                evidence_id=evidence_id,
                extraction_method=CATALOG_INGESTION_EXTRACTION_METHOD,
                confidence=None,
                normalization_rule=CATALOG_INGESTION_NORMALIZATION_RULE,
            )
            previous = existing.get(fact_id)
            if previous is None:
                store.save_catalog_candidate_fact(fact)
                existing[fact_id] = fact
            elif previous != fact:
                raise ValueError(
                    f"evidence {evidence_id!r} already produced "
                    f"a different {attribute!r} observation"
                )


def _review_comparisons(
    comparisons: tuple[CatalogIngestionComparison, ...],
) -> tuple[CatalogReviewComparison, ...]:
    return tuple(
        CatalogReviewComparison(
            vehicle_id=item.vehicle_id,
            outcome=item.outcome.value,
            reason=item.reason,
        )
        for item in comparisons
    )


def ingest_catalog_multisource_v2(
    store: CatalogStore,
    envelope: CatalogMultisourceV2Envelope,
) -> CatalogMultisourceIngestionResult:
    if not isinstance(envelope, CatalogMultisourceV2Envelope):
        raise ValueError("envelope must be a CatalogMultisourceV2Envelope")

    identity = catalog_identity_from_record(envelope.vehicle)
    comparisons = tuple(
        CatalogIngestionComparison(vehicle_id, decision.outcome, decision.reason)
        for vehicle_id, existing_identity in _catalog_entries(store)
        for decision in (
            resolve_catalog_pair_with_structural_precedence(identity, existing_identity),
        )
    )
    matches = tuple(
        comparison.vehicle_id
        for comparison in comparisons
        if comparison.outcome is CatalogMatchOutcome.MATCH
    )
    reviews = tuple(
        comparison.vehicle_id
        for comparison in comparisons
        if comparison.outcome is CatalogMatchOutcome.REVIEW
    )

    review_vehicle_ids: tuple[str, ...] = ()
    if len(matches) == 1:
        action = CatalogIngestionAction.MATCHED
        vehicle_id: str | None = matches[0]
    elif len(matches) > 1:
        action = CatalogIngestionAction.REVIEW
        vehicle_id = None
        review_vehicle_ids = matches
    elif reviews:
        action = CatalogIngestionAction.REVIEW
        vehicle_id = None
        review_vehicle_ids = reviews
    else:
        evidence_ids_for_publication = tuple(item.id for item in envelope.evidence)
        validate_catalog_publication_change(
            None,
            identity,
            action=CatalogPublicationAction.CREATE,
            decision_status=DecisionStatus.EVIDENCE_BACKED,
            evidence_ids=evidence_ids_for_publication,
        )
        action = CatalogIngestionAction.CREATED
        vehicle_id = None

    evidence_ids = tuple(item.id for item in envelope.evidence)
    review_id: str | None = None
    review_queue = (
        CatalogMultisourceReviewQueue(store)
        if action is CatalogIngestionAction.REVIEW
        else None
    )
    with store.transaction():
        for source in envelope.sources:
            _ensure_source(store, source)
        for evidence in envelope.evidence:
            _ensure_evidence(store, evidence)

        if action is CatalogIngestionAction.CREATED:
            vehicle_id = store.create_catalog_vehicle(identity)
        elif action is CatalogIngestionAction.REVIEW:
            assert review_queue is not None
            task = review_queue.enqueue(
                evidence_ids=evidence_ids,
                identity=identity,
                candidate_vehicle_ids=review_vehicle_ids,
                comparisons=_review_comparisons(comparisons),
                field_evidence=envelope.field_evidence,
            )
            review_id = task.id

        if vehicle_id is not None:
            _save_field_evidence_candidates(
                store,
                vehicle_id,
                identity,
                envelope.field_evidence,
            )

    return CatalogMultisourceIngestionResult(
        action=action,
        identity=identity,
        evidence_ids=evidence_ids,
        vehicle_id=vehicle_id,
        comparisons=comparisons,
        review_vehicle_ids=review_vehicle_ids,
        review_id=review_id,
    )


def _require_review_task(
    queue: CatalogMultisourceReviewQueue,
    review_id: str,
) -> CatalogMultisourceReviewTask:
    task = queue.get(review_id)
    if task is None:
        raise ValueError("catalog multisource review task does not exist")
    return task


def resolve_catalog_multisource_review_match(
    store: CatalogStore,
    review_id: str,
    vehicle_id: str,
    *,
    actor_id: str,
    reason: str,
) -> CatalogMultisourceReviewTask:
    queue = CatalogMultisourceReviewQueue(store)
    task = _require_review_task(queue, review_id)
    canonical_target = store.resolve_catalog_id(vehicle_id)

    if task.state is CatalogReviewState.RESOLVED:
        if (
            task.resolution_action is CatalogReviewResolutionAction.MATCHED
            and task.resolution_vehicle_id == canonical_target
            and task.resolved_by == actor_id.strip()
            and task.resolution_reason == reason.strip()
        ):
            return task
        raise ValueError("catalog multisource review task is already resolved")

    candidates = {
        store.resolve_catalog_id(candidate)
        for candidate in task.candidate_vehicle_ids
    }
    if canonical_target not in candidates:
        raise ValueError("selected vehicle is not a candidate for this review")
    if store.get_catalog_vehicle(canonical_target) is None:
        raise ValueError("selected catalog vehicle does not exist")

    with store.transaction():
        _save_field_evidence_candidates(
            store,
            canonical_target,
            task.identity,
            task.field_evidence,
        )
        return queue.resolve(
            review_id,
            action=CatalogReviewResolutionAction.MATCHED,
            vehicle_id=canonical_target,
            actor_id=actor_id,
            reason=reason,
        )


def resolve_catalog_multisource_review_create(
    store: CatalogStore,
    review_id: str,
    *,
    actor_id: str,
    reason: str,
) -> CatalogMultisourceReviewTask:
    queue = CatalogMultisourceReviewQueue(store)
    task = _require_review_task(queue, review_id)

    if task.state is CatalogReviewState.RESOLVED:
        if (
            task.resolution_action is CatalogReviewResolutionAction.CREATED
            and task.resolved_by == actor_id.strip()
            and task.resolution_reason == reason.strip()
        ):
            return task
        raise ValueError("catalog multisource review task is already resolved")

    validate_catalog_publication_change(
        None,
        task.identity,
        action=CatalogPublicationAction.CREATE,
        decision_status=DecisionStatus.EVIDENCE_BACKED,
        evidence_ids=task.evidence_ids,
    )

    with store.transaction():
        vehicle_id = store.create_catalog_vehicle(task.identity)
        _save_field_evidence_candidates(
            store,
            vehicle_id,
            task.identity,
            task.field_evidence,
        )
        return queue.resolve(
            review_id,
            action=CatalogReviewResolutionAction.CREATED,
            vehicle_id=vehicle_id,
            actor_id=actor_id,
            reason=reason,
        )


__all__ = [
    "CatalogMultisourceIngestionError",
    "CatalogMultisourceIngestionResult",
    "ingest_catalog_multisource_v2",
    "resolve_catalog_multisource_review_create",
    "resolve_catalog_multisource_review_match",
]
