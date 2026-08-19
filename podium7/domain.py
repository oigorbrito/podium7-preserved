from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


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


@dataclass(frozen=True)
class RawEvidence:
    id: str
    source_id: str
    locator: str
    retrieved_at: datetime
    acquisition_method: str
    raw_content_ref: str


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
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.attribute.strip():
            raise ValueError("attribute is required")


@dataclass(frozen=True)
class ProvenanceRecord:
    entity_id: str
    activity_id: str
    agent_id: str | None = None
    was_derived_from: tuple[str, ...] = ()
    was_generated_by: str | None = None
    was_associated_with: str | None = None


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
        if not self.candidate_references:
            raise ValueError("canonical facts require at least one candidate reference")
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
        if len(self.candidate_references) < 2:
            raise ValueError("a conflict requires at least two candidate references")
        if self.resolution_state is ConflictState.RESOLVED and self.selected_candidate_id is None:
            raise ValueError("resolved conflicts require selected_candidate_id")
        if self.selected_candidate_id is not None and self.selected_candidate_id not in self.candidate_references:
            raise ValueError("selected candidate must belong to candidate_references")
