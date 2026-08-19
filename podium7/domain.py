from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
from typing import Any


def _require_text(value: str, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} is required")


def _require_optional_text(value: str | None, field: str) -> None:
    if value is not None and not value.strip():
        raise ValueError(f"{field} must be non-empty when provided")


def _require_unique_texts(values: tuple[str, ...], field: str) -> None:
    for value in values:
        _require_text(value, field)
    if len(set(values)) != len(values):
        raise ValueError(f"{field} must not contain duplicates")


def _require_json_value(value: Any, field: str) -> None:
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be strict JSON-compatible") from exc


class DecisionStatus(str, Enum):
    EVIDENCE_BACKED = "EVIDENCE_BACKED"
    HYPOTHESIS = "HYPOTHESIS"
    LOCALLY_VERIFIED = "LOCALLY_VERIFIED"
    ENGINEERING_CHOICE = "ENGINEERING_CHOICE"
    UNKNOWN = "UNKNOWN"


class EntityKind(str, Enum):
    MAKE = "Make"
    MODEL = "Model"
    GENERATION = "Generation"
    VARIANT = "Variant"
    POWERTRAIN = "Powertrain"


class ConflictState(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED = "RESOLVED"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    locator: str

    def __post_init__(self) -> None:
        _require_text(self.id, "source id")
        _require_text(self.name, "source name")
        _require_text(self.locator, "source locator")


@dataclass(frozen=True)
class RawEvidence:
    id: str
    source_id: str
    locator: str
    retrieved_at: datetime
    acquisition_method: str
    raw_content_ref: str

    def __post_init__(self) -> None:
        _require_text(self.id, "evidence id")
        _require_text(self.source_id, "evidence source_id")
        _require_text(self.locator, "evidence locator")
        _require_text(self.acquisition_method, "evidence acquisition_method")
        _require_text(self.raw_content_ref, "evidence raw_content_ref")
        if self.retrieved_at.tzinfo is None or self.retrieved_at.utcoffset() is None:
            raise ValueError("evidence retrieved_at must be timezone-aware")


@dataclass(frozen=True)
class AutomotiveIdentity:
    kind: EntityKind
    make: str
    model: str | None = None
    generation: str | None = None
    variant: str | None = None
    powertrain: str | None = None
    market: str | None = None
    year_from: int | None = None
    year_to: int | None = None
    aliases: tuple[str, ...] = ()
    engine_identifiers: tuple[str, ...] = ()
    external_identifiers: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.year_from is not None and self.year_to is not None and self.year_from > self.year_to:
            raise ValueError("year_from cannot be greater than year_to")
        if not self.make.strip():
            raise ValueError("make is required")


@dataclass(frozen=True)
class CandidateFact:
    id: str
    entity_candidate_id: str
    attribute: str
    raw_value: Any
    normalized_value: Any
    unit: str | None
    evidence_id: str
    extraction_method: str
    confidence: float | None = None
    normalization_rule: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "candidate fact id")
        _require_text(self.entity_candidate_id, "candidate entity_candidate_id")
        _require_text(self.attribute, "attribute")
        _require_text(self.evidence_id, "candidate evidence_id")
        _require_text(self.extraction_method, "candidate extraction_method")
        _require_optional_text(self.unit, "candidate unit")
        _require_optional_text(self.normalization_rule, "candidate normalization_rule")
        _require_json_value(self.raw_value, "candidate raw_value")
        _require_json_value(self.normalized_value, "candidate normalized_value")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class ProvenanceRecord:
    entity_id: str
    activity_id: str
    agent_id: str | None = None
    was_derived_from: tuple[str, ...] = ()
    was_generated_by: str | None = None
    was_associated_with: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.entity_id, "provenance entity_id")
        _require_text(self.activity_id, "provenance activity_id")
        _require_optional_text(self.agent_id, "provenance agent_id")
        _require_optional_text(self.was_generated_by, "provenance was_generated_by")
        _require_optional_text(self.was_associated_with, "provenance was_associated_with")
        _require_unique_texts(self.was_derived_from, "provenance derivation reference")


@dataclass(frozen=True)
class CanonicalFact:
    id: str
    entity_id: str
    attribute: str
    accepted_value: Any
    candidate_references: tuple[str, ...]
    fusion_decision: str
    provenance: ProvenanceRecord

    def __post_init__(self) -> None:
        _require_text(self.id, "canonical fact id")
        _require_text(self.entity_id, "canonical entity_id")
        _require_text(self.attribute, "canonical attribute")
        _require_text(self.fusion_decision, "canonical fusion_decision")
        _require_json_value(self.accepted_value, "canonical accepted_value")
        if not self.candidate_references:
            raise ValueError("canonical facts require at least one candidate reference")
        _require_unique_texts(self.candidate_references, "canonical candidate reference")
        if self.provenance.entity_id != self.entity_id:
            raise ValueError("canonical fact provenance must reference the same entity")
        missing_derivations = tuple(
            reference
            for reference in self.candidate_references
            if reference not in self.provenance.was_derived_from
        )
        if missing_derivations:
            raise ValueError(
                "canonical fact provenance must derive from every candidate reference: "
                + ", ".join(missing_derivations)
            )


@dataclass(frozen=True)
class Conflict:
    id: str
    attribute: str
    candidate_references: tuple[str, ...]
    reason: str
    resolution_state: ConflictState = ConflictState.UNRESOLVED
    selected_candidate_id: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.id, "conflict id")
        _require_text(self.attribute, "conflict attribute")
        _require_text(self.reason, "conflict reason")
        if len(self.candidate_references) < 2:
            raise ValueError("a conflict requires at least two candidate references")
        _require_unique_texts(self.candidate_references, "conflict candidate reference")
        if self.resolution_state is ConflictState.RESOLVED and self.selected_candidate_id is None:
            raise ValueError("resolved conflicts require selected_candidate_id")
        _require_optional_text(self.selected_candidate_id, "conflict selected_candidate_id")
        if self.selected_candidate_id is not None and self.selected_candidate_id not in self.candidate_references:
            raise ValueError("selected candidate must belong to candidate_references")
