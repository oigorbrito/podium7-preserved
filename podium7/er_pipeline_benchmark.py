from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .catalog import CatalogMatchOutcome


REPORT_SCHEMA = "podium7.er-pipeline-benchmark.v1"


@dataclass(frozen=True)
class ERPipelineCase:
    case_id: str
    expected: CatalogMatchOutcome
    candidate_retained: bool
    verifier_outcome: CatalogMatchOutcome | None

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be non-empty text")
        if not isinstance(self.expected, CatalogMatchOutcome):
            raise ValueError("expected must be CatalogMatchOutcome")
        if not isinstance(self.candidate_retained, bool):
            raise ValueError("candidate_retained must be boolean")
        if self.candidate_retained and not isinstance(self.verifier_outcome, CatalogMatchOutcome):
            raise ValueError("retained candidates require a verifier outcome")
        if not self.candidate_retained and self.verifier_outcome is not None:
            raise ValueError("filtered candidates cannot have a verifier outcome")


@dataclass(frozen=True)
class ERPipelineCost:
    latency_ms: int | None = None
    peak_memory_bytes: int | None = None

    def __post_init__(self) -> None:
        for name, value in (("latency_ms", self.latency_ms), ("peak_memory_bytes", self.peak_memory_bytes)):
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer when provided")


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def evaluate_er_pipeline(
    cases: Iterable[ERPipelineCase],
    *,
    cost: ERPipelineCost = ERPipelineCost(),
) -> dict[str, Any]:
    case_list = tuple(cases)
    if not case_list:
        raise ValueError("at least one ER pipeline case is required")
    if any(not isinstance(case, ERPipelineCase) for case in case_list):
        raise ValueError("all items must be ERPipelineCase instances")
    ids = [case.case_id for case in case_list]
    if len(ids) != len(set(ids)):
        raise ValueError("case_id values must be unique")

    total = len(case_list)
    retained = sum(case.candidate_retained for case in case_list)
    expected_match = sum(case.expected is CatalogMatchOutcome.MATCH for case in case_list)
    retained_true_match = sum(
        case.expected is CatalogMatchOutcome.MATCH and case.candidate_retained
        for case in case_list
    )

    verifier_true_match = sum(
        case.candidate_retained
        and case.expected is CatalogMatchOutcome.MATCH
        and case.verifier_outcome is CatalogMatchOutcome.MATCH
        for case in case_list
    )
    verifier_predicted_match = sum(
        case.candidate_retained and case.verifier_outcome is CatalogMatchOutcome.MATCH
        for case in case_list
    )
    verifier_expected_match = sum(
        case.candidate_retained and case.expected is CatalogMatchOutcome.MATCH
        for case in case_list
    )

    observations: list[dict[str, Any]] = []
    true_match = false_merge = missed_match = ambiguous_overcommit = predicted_review = 0
    for case in case_list:
        end_to_end = (
            case.verifier_outcome
            if case.candidate_retained
            else CatalogMatchOutcome.NO_MATCH
        )
        if case.expected is CatalogMatchOutcome.MATCH and end_to_end is CatalogMatchOutcome.MATCH:
            true_match += 1
        if case.expected is CatalogMatchOutcome.NO_MATCH and end_to_end is CatalogMatchOutcome.MATCH:
            false_merge += 1
        if case.expected is CatalogMatchOutcome.MATCH and end_to_end is not CatalogMatchOutcome.MATCH:
            missed_match += 1
        if case.expected is CatalogMatchOutcome.REVIEW and end_to_end is not CatalogMatchOutcome.REVIEW:
            ambiguous_overcommit += 1
        if end_to_end is CatalogMatchOutcome.REVIEW:
            predicted_review += 1
        observations.append(
            {
                "caseId": case.case_id,
                "expected": case.expected.value,
                "candidateRetained": case.candidate_retained,
                "verifierOutcome": None if case.verifier_outcome is None else case.verifier_outcome.value,
                "endToEndOutcome": end_to_end.value,
            }
        )

    end_to_end_predicted_match = sum(
        item["endToEndOutcome"] == CatalogMatchOutcome.MATCH.value
        for item in observations
    )

    return {
        "schema": REPORT_SCHEMA,
        "metrics": {
            "caseCount": total,
            "retainedCandidateCount": retained,
            "candidateReductionRatio": 1 - (retained / total),
            "blockingRecall": _rate(retained_true_match, expected_match),
            "verificationPrecision": _rate(verifier_true_match, verifier_predicted_match),
            "verificationRecall": _rate(verifier_true_match, verifier_expected_match),
            "endToEndMatchPrecision": _rate(true_match, end_to_end_predicted_match),
            "endToEndMatchRecall": _rate(true_match, expected_match),
            "falseMergeCount": false_merge,
            "missedMatchCount": missed_match,
            "ambiguousOvercommitCount": ambiguous_overcommit,
            "reviewRate": predicted_review / total,
            "latencyMs": cost.latency_ms,
            "peakMemoryBytes": cost.peak_memory_bytes,
        },
        "cases": observations,
    }


__all__ = ["ERPipelineCase", "ERPipelineCost", "REPORT_SCHEMA", "evaluate_er_pipeline"]
