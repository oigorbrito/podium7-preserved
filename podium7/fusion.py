from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .domain import CandidateFact, CanonicalFact, Conflict, ProvenanceRecord


@dataclass(frozen=True)
class FusionResult:
    canonical_fact: CanonicalFact | None
    conflict: Conflict | None


def _stable_id(prefix: str, material: str) -> str:
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _normalized_key(fact: CandidateFact) -> str:
    return json.dumps(
        {"value": fact.normalized_value, "unit": fact.unit},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )


def fuse_candidates(entity_id: str, candidates: list[CandidateFact]) -> FusionResult:
    if not candidates:
        raise ValueError("at least one candidate is required")

    attributes = {candidate.attribute for candidate in candidates}
    if len(attributes) != 1:
        raise ValueError("all candidates must describe the same attribute")

    attribute = candidates[0].attribute
    ordered = sorted(candidates, key=lambda candidate: candidate.id)
    references = tuple(candidate.id for candidate in ordered)
    decision_material = f"{entity_id}|{attribute}|{'|'.join(references)}"

    if len(ordered) == 1:
        candidate = ordered[0]
        provenance = ProvenanceRecord(
            entity_id=entity_id,
            activity_id=_stable_id("fusion-activity", decision_material),
            was_derived_from=references,
            was_generated_by="fusion.single_candidate.v1",
        )
        canonical = CanonicalFact(
            id=_stable_id("canonical", decision_material),
            entity_id=entity_id,
            attribute=attribute,
            accepted_value={"value": candidate.normalized_value, "unit": candidate.unit},
            candidate_references=references,
            fusion_decision="single-candidate.v1",
            provenance=provenance,
        )
        return FusionResult(canonical, None)

    normalized_keys = {_normalized_key(candidate) for candidate in ordered}
    if len(normalized_keys) == 1:
        candidate = ordered[0]
        provenance = ProvenanceRecord(
            entity_id=entity_id,
            activity_id=_stable_id("fusion-activity", decision_material),
            was_derived_from=references,
            was_generated_by="fusion.unanimous_agreement.v1",
        )
        canonical = CanonicalFact(
            id=_stable_id("canonical", decision_material),
            entity_id=entity_id,
            attribute=attribute,
            accepted_value={"value": candidate.normalized_value, "unit": candidate.unit},
            candidate_references=references,
            fusion_decision="unanimous-normalized-agreement.v1",
            provenance=provenance,
        )
        return FusionResult(canonical, None)

    conflict = Conflict(
        id=_stable_id("conflict", decision_material),
        attribute=attribute,
        candidate_references=references,
        reason="normalized candidate values disagree",
    )
    return FusionResult(None, conflict)
