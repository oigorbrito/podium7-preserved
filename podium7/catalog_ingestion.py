from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
from typing import Any

from .catalog import (
    CatalogMatchOutcome,
    CatalogPublicationAction,
    CatalogStore,
    CatalogVehicleIdentity,
    ExternalIdentifier,
    validate_catalog_publication_change,
)
from .catalog_resolution_precedence import resolve_catalog_pair_with_structural_precedence
from .catalog_review import (
    CatalogReviewComparison,
    CatalogReviewQueue,
    CatalogReviewResolutionAction,
    CatalogReviewState,
    CatalogReviewTask,
)
from .catalog_review_cause import snapshot_review_causes
from .domain import CandidateFact, DecisionStatus, RawEvidence, Source


CATALOG_INGESTION_EXTRACTION_METHOD = "catalog-ingestion-flow-v1"
CATALOG_INGESTION_NORMALIZATION_RULE = "catalog-identity.clean-whitespace.v1"
CATALOG_INGESTION_PAGE_SIZE = 100


class CatalogIngestionAction(str, Enum):
    CREATED = "CREATED"
    MATCHED = "MATCHED"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class CatalogIngestionComparison:
    vehicle_id: str
    outcome: CatalogMatchOutcome
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "vehicleId": self.vehicle_id,
            "outcome": self.outcome.value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CatalogIngestionResult:
    action: CatalogIngestionAction
    identity: CatalogVehicleIdentity
    evidence_id: str
    vehicle_id: str | None
    comparisons: tuple[CatalogIngestionComparison, ...]
    review_vehicle_ids: tuple[str, ...] = ()
    review_id: str | None = None

    def to_payload(self) -> dict[str, Any]:
        identity = asdict(self.identity)
        identity["aliases"] = list(self.identity.aliases)
        identity["engine_identifiers"] = list(self.identity.engine_identifiers)
        identity["external_identifiers"] = [
            {"namespace": item.namespace, "value": item.value}
            for item in self.identity.external_identifiers
        ]
        return {
            "action": self.action.value,
            "vehicleId": self.vehicle_id,
            "evidenceId": self.evidence_id,
            "reviewId": self.review_id,
            "identity": identity,
            "reviewVehicleIds": list(self.review_vehicle_ids),
            "comparisons": [comparison.to_payload() for comparison in self.comparisons],
        }


_TEXT_FIELDS = (
    "make",
    "model",
    "generation",
    "variant",
    "powertrain",
    "transmission",
    "body_style",
    "market",
)
_YEAR_FIELDS = (
    "manufacture_year_from",
    "manufacture_year_to",
    "model_year_from",
    "model_year_to",
)
_COLLECTION_FIELDS = ("aliases", "engine_identifiers")
_ALLOWED_FIELDS = set(_TEXT_FIELDS + _YEAR_FIELDS + _COLLECTION_FIELDS + ("external_identifiers",))


def _clean_text(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text")
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        raise ValueError(f"{field} must be non-empty text")
    return cleaned


def _clean_text_sequence(value: Any, field: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{field} must be an array of text values")
    return tuple(_clean_text(item, field) for item in value)


def catalog_identity_from_record(record: Mapping[str, Any]) -> CatalogVehicleIdentity:
    if not isinstance(record, Mapping):
        raise ValueError("vehicle record must be an object")
    unknown = sorted(set(record) - _ALLOWED_FIELDS)
    if unknown:
        raise ValueError("unsupported vehicle fields: " + ", ".join(unknown))

    payload: dict[str, Any] = {}
    for field in _TEXT_FIELDS:
        value = record.get(field)
        if value is not None:
            payload[field] = _clean_text(value, field)

    for field in _YEAR_FIELDS:
        if field in record and record[field] is not None:
            payload[field] = record[field]

    for field in _COLLECTION_FIELDS:
        if field in record:
            payload[field] = _clean_text_sequence(record[field], field)

    if "external_identifiers" in record:
        raw_identifiers = record["external_identifiers"]
        if isinstance(raw_identifiers, (str, bytes)) or not isinstance(raw_identifiers, Sequence):
            raise ValueError("external_identifiers must be an array")
        identifiers: list[ExternalIdentifier] = []
        for index, raw_identifier in enumerate(raw_identifiers):
            if not isinstance(raw_identifier, Mapping):
                raise ValueError(f"external_identifiers[{index}] must be an object")
            unknown_keys = sorted(set(raw_identifier) - {"namespace", "value"})
            if unknown_keys:
                raise ValueError(
                    f"unsupported external_identifiers[{index}] fields: "
                    + ", ".join(unknown_keys)
                )
            identifiers.append(
                ExternalIdentifier(
                    namespace=_clean_text(
                        raw_identifier.get("namespace"),
                        "external identifier namespace",
                    ),
                    value=_clean_text(
                        raw_identifier.get("value"),
                        "external identifier value",
                    ),
                )
            )
        payload["external_identifiers"] = tuple(identifiers)

    return CatalogVehicleIdentity(**payload)


def _catalog_entries(store: CatalogStore) -> list[tuple[str, CatalogVehicleIdentity]]:
    entries: list[tuple[str, CatalogVehicleIdentity]] = []
    cursor: str | None = None
    while True:
        ids = store.catalog_vehicle_ids_page(
            after_id=cursor,
            limit=CATALOG_INGESTION_PAGE_SIZE,
        )
        if not ids:
            break
        for vehicle_id in ids:
            identity = store.get_catalog_vehicle(vehicle_id)
            if identity is None:
                raise RuntimeError(
                    f"catalog vehicle disappeared during ingestion: {vehicle_id}"
                )
            entries.append((vehicle_id, identity))
        if len(ids) < CATALOG_INGESTION_PAGE_SIZE:
            break
        cursor = ids[-1]
    return entries


def _ensure_source_and_evidence(
    store: CatalogStore,
    source: Source,
    evidence: RawEvidence,
) -> None:
    if evidence.source_id != source.id:
        raise ValueError("evidence source_id must match source id")

    existing_source = store.get_source(source.id)
    if existing_source is None:
        store.save_source(source)
    elif existing_source != source:
        raise ValueError(
            f"source id {source.id!r} already exists with different metadata"
        )

    existing_evidence = store.get_raw_evidence(evidence.id)
    if existing_evidence is None:
        store.save_raw_evidence(evidence)
    elif existing_evidence != evidence:
        raise ValueError(
            f"evidence id {evidence.id!r} already exists with different metadata"
        )


def _observation_values(
    identity: CatalogVehicleIdentity,
) -> tuple[tuple[str, Any], ...]:
    observations: list[tuple[str, Any]] = []
    for field in _TEXT_FIELDS + _YEAR_FIELDS:
        value = getattr(identity, field)
        if value is not None:
            observations.append((field, value))
    if identity.aliases:
        observations.append(("aliases", list(identity.aliases)))
    if identity.engine_identifiers:
        observations.append(("engine_identifiers", list(identity.engine_identifiers)))
    if identity.external_identifiers:
        observations.append(
            (
                "external_identifiers",
                [
                    {"namespace": item.namespace, "value": item.value}
                    for item in identity.external_identifiers
                ],
            )
        )
    return tuple(observations)


def _candidate_id(evidence_id: str, vehicle_id: str, attribute: str) -> str:
    material = f"{evidence_id}|{vehicle_id}|{attribute}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"catalog_candidate:{digest}"


def _save_observation_candidates(
    store: CatalogStore,
    vehicle_id: str,
    identity: CatalogVehicleIdentity,
    evidence_id: str,
) -> None:
    existing = {
        fact.id: fact for fact in store.catalog_candidates_for_entity(vehicle_id)
    }
    for attribute, value in _observation_values(identity):
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
        elif previous != fact:
            raise ValueError(
                f"evidence {evidence_id!r} already produced "
                f"a different {attribute!r} observation"
            )


def _review_comparisons(
    comparisons: Sequence[CatalogIngestionComparison],
) -> tuple[CatalogReviewComparison, ...]:
    return tuple(
        CatalogReviewComparison(
            vehicle_id=item.vehicle_id,
            outcome=item.outcome.value,
            reason=item.reason,
        )
        for item in comparisons
    )


def ingest_catalog_record(
    store: CatalogStore,
    record: Mapping[str, Any],
    *,
    source: Source,
    evidence: RawEvidence,
) -> CatalogIngestionResult:
    identity = catalog_identity_from_record(record)
    if evidence.source_id != source.id:
        raise ValueError("evidence source_id must match source id")

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

    if len(matches) == 1:
        action = CatalogIngestionAction.MATCHED
        vehicle_id: str | None = matches[0]
        review_vehicle_ids: tuple[str, ...] = ()
    elif len(matches) > 1:
        action = CatalogIngestionAction.REVIEW
        vehicle_id = None
        review_vehicle_ids = matches
    elif reviews:
        action = CatalogIngestionAction.REVIEW
        vehicle_id = None
        review_vehicle_ids = reviews
    else:
        validate_catalog_publication_change(
            None,
            identity,
            action=CatalogPublicationAction.CREATE,
            decision_status=DecisionStatus.EVIDENCE_BACKED,
            evidence_ids=(evidence.id,),
        )
        action = CatalogIngestionAction.CREATED
        vehicle_id = None
        review_vehicle_ids = ()

    review_id: str | None = None
    review_queue = (
        CatalogReviewQueue(store)
        if action is CatalogIngestionAction.REVIEW
        else None
    )

    with store.transaction():
        _ensure_source_and_evidence(store, source, evidence)
        if action is CatalogIngestionAction.CREATED:
            vehicle_id = store.create_catalog_vehicle(identity)
        elif action is CatalogIngestionAction.REVIEW:
            assert review_queue is not None
            review_comparisons = _review_comparisons(comparisons)
            task = review_queue.enqueue(
                evidence_id=evidence.id,
                identity=identity,
                candidate_vehicle_ids=review_vehicle_ids,
                comparisons=review_comparisons,
            )
            snapshot_review_causes(
                store,
                review_id=task.id,
                comparisons=review_comparisons,
                candidate_vehicle_ids=review_vehicle_ids,
            )
            review_id = task.id

        if vehicle_id is not None:
            _save_observation_candidates(
                store,
                vehicle_id,
                identity,
                evidence.id,
            )

    return CatalogIngestionResult(
        action=action,
        identity=identity,
        evidence_id=evidence.id,
        vehicle_id=vehicle_id,
        comparisons=comparisons,
        review_vehicle_ids=review_vehicle_ids,
        review_id=review_id,
    )


def _require_review_task(
    queue: CatalogReviewQueue,
    review_id: str,
) -> CatalogReviewTask:
    task = queue.get(review_id)
    if task is None:
        raise ValueError("catalog review task does not exist")
    return task


def resolve_catalog_review_match(
    store: CatalogStore,
    review_id: str,
    vehicle_id: str,
    *,
    actor_id: str,
    reason: str,
) -> CatalogReviewTask:
    queue = CatalogReviewQueue(store)
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
        raise ValueError("catalog review task is already resolved")

    candidates = {
        store.resolve_catalog_id(candidate)
        for candidate in task.candidate_vehicle_ids
    }
    if canonical_target not in candidates:
        raise ValueError("selected vehicle is not a candidate for this review")
    if store.get_catalog_vehicle(canonical_target) is None:
        raise ValueError("selected catalog vehicle does not exist")

    with store.transaction():
        _save_observation_candidates(
            store,
            canonical_target,
            task.identity,
            task.evidence_id,
        )
        return queue.resolve(
            review_id,
            action=CatalogReviewResolutionAction.MATCHED,
            vehicle_id=canonical_target,
            actor_id=actor_id,
            reason=reason,
        )


def resolve_catalog_review_create(
    store: CatalogStore,
    review_id: str,
    *,
    actor_id: str,
    reason: str,
) -> CatalogReviewTask:
    queue = CatalogReviewQueue(store)
    task = _require_review_task(queue, review_id)

    if task.state is CatalogReviewState.RESOLVED:
        if (
            task.resolution_action is CatalogReviewResolutionAction.CREATED
            and task.resolved_by == actor_id.strip()
            and task.resolution_reason == reason.strip()
        ):
            return task
        raise ValueError("catalog review task is already resolved")

    validate_catalog_publication_change(
        None,
        task.identity,
        action=CatalogPublicationAction.CREATE,
        decision_status=DecisionStatus.EVIDENCE_BACKED,
        evidence_ids=(task.evidence_id,),
    )

    with store.transaction():
        vehicle_id = store.create_catalog_vehicle(task.identity)
        _save_observation_candidates(
            store,
            vehicle_id,
            task.identity,
            task.evidence_id,
        )
        return queue.resolve(
            review_id,
            action=CatalogReviewResolutionAction.CREATED,
            vehicle_id=vehicle_id,
            actor_id=actor_id,
            reason=reason,
        )


__all__ = [
    "CATALOG_INGESTION_EXTRACTION_METHOD",
    "CatalogIngestionAction",
    "CatalogIngestionComparison",
    "CatalogIngestionResult",
    "catalog_identity_from_record",
    "ingest_catalog_record",
    "resolve_catalog_review_create",
    "resolve_catalog_review_match",
]
