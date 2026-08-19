from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .domain import Conflict, ConflictState
from .identity import MatchOutcome, ResolutionDecision


class ReviewAction(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class ReviewDecision:
    action: ReviewAction
    reason: str


def review_identity(decision: ResolutionDecision) -> ReviewDecision:
    if decision.outcome is MatchOutcome.UNRESOLVED:
        return ReviewDecision(ReviewAction.REVIEW, "identity ambiguity")
    return ReviewDecision(ReviewAction.AUTOMATIC, f"deterministic identity outcome: {decision.outcome.value}")


def review_conflict(conflict: Conflict) -> ReviewDecision:
    if conflict.resolution_state in {ConflictState.UNRESOLVED, ConflictState.REVIEW}:
        return ReviewDecision(ReviewAction.REVIEW, "unresolved fact conflict")
    return ReviewDecision(ReviewAction.AUTOMATIC, "conflict already resolved with traceable selection")


def review_evidence(*, source_known: bool, schema_valid: bool, anomaly: bool = False) -> ReviewDecision:
    if not source_known:
        return ReviewDecision(ReviewAction.REVIEW, "new or unknown source")
    if not schema_valid:
        return ReviewDecision(ReviewAction.REVIEW, "schema validation failed")
    if anomaly:
        return ReviewDecision(ReviewAction.REVIEW, "anomaly detected")
    return ReviewDecision(ReviewAction.AUTOMATIC, "known source and valid schema without anomaly")
