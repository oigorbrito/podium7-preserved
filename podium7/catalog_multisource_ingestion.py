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
from .catalog_multisource_v2 import CatalogMultisourceV2Envelope
from .catalog_resolution_precedence import resolve_catalog_pair_with_structural_precedence
from .domain import CandidateFact, DecisionStatus, RawEvidence, Source


MULTISOURCE_REVIEW_NOT_IMPLEMENTED = "MULTISOURCE_REVIEW_NOT_IMPLEMENTED"


class CatalogMultisourceIngestionError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CatalogMultisourceIngestionResult:
    action: CatalogIngestionAction
    identity: CatalogVehicleIdentity
    evidence_ids: tuple[str, ...]
    vehicle_id: str
    comparisons: tuple[CatalogIngestionComparison, ...]


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

    if len(matches) == 1:
        action = CatalogIngestionAction.MATCHED
        vehicle_id = matches[0]
    elif len(matches) > 1 or reviews:
        raise CatalogMultisourceIngestionError(
            MULTISOURCE_REVIEW_NOT_IMPLEMENTED,
            "multi-evidence REVIEW requires the dedicated review field-binding path",
        )
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
        vehicle_id = ""

    evidence_ids = tuple(item.id for item in envelope.evidence)
    with store.transaction():
        for source in envelope.sources:
            _ensure_source(store, source)
        for evidence in envelope.evidence:
            _ensure_evidence(store, evidence)

        if action is CatalogIngestionAction.CREATED:
            vehicle_id = store.create_catalog_vehicle(identity)

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
    )


__all__ = [
    "MULTISOURCE_REVIEW_NOT_IMPLEMENTED",
    "CatalogMultisourceIngestionError",
    "CatalogMultisourceIngestionResult",
    "ingest_catalog_multisource_v2",
]
