from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .domain import CandidateFact
from .fusion import fuse_candidates


@dataclass(frozen=True)
class SourceCandidate:
    source_id: str
    fact: CandidateFact

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("source_id is required")
        if not isinstance(self.fact, CandidateFact):
            raise ValueError("fact must be a CandidateFact")


@dataclass(frozen=True)
class MultiSourceCase:
    case_id: str
    entity_id: str
    attribute: str
    candidates: tuple[SourceCandidate, ...]
    expected_disposition: str
    rationale: str

    def __post_init__(self) -> None:
        if self.expected_disposition not in {"CANONICAL", "CONFLICT", "REVIEW"}:
            raise ValueError("unsupported expected disposition")
        for field_name, value in (
            ("case_id", self.case_id),
            ("entity_id", self.entity_id),
            ("attribute", self.attribute),
            ("rationale", self.rationale),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
        if not isinstance(self.candidates, tuple):
            raise ValueError("candidates must be a tuple of SourceCandidate values")
        if any(not isinstance(item, SourceCandidate) for item in self.candidates):
            raise ValueError("candidates must contain SourceCandidate values")
        if any(item.fact.attribute != self.attribute for item in self.candidates):
            raise ValueError("all candidate facts must match the case attribute")
        fact_ids = [item.fact.id for item in self.candidates]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("candidate fact ids must be unique within a validation case")


def evaluate_multisource_cases(cases: Iterable[MultiSourceCase]) -> dict:
    case_list = tuple(cases)
    if not case_list:
        raise ValueError("at least one validation case is required")
    if any(not isinstance(case, MultiSourceCase) for case in case_list):
        raise ValueError("validation cases must be MultiSourceCase values")
    case_ids = [case.case_id for case in case_list]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("validation case ids must be unique")

    results = []
    source_contribution: dict[str, int] = {}
    conflict_states: Counter[str] = Counter()
    corroborated = conflicts = reviews = canonical = provenance_complete = incorrect = 0
    provenance_applicable = 0

    for case in case_list:
        sources = tuple(sorted({item.source_id for item in case.candidates}))
        for source_id in sources:
            source_contribution[source_id] = source_contribution.get(source_id, 0) + 1

        conflict_state: str | None = None
        if not case.candidates:
            disposition = "REVIEW"
            candidate_refs: tuple[str, ...] = ()
            provenance_ok: bool | None = None
        else:
            provenance_applicable += 1
            expected_refs = {item.fact.id for item in case.candidates}
            fusion = fuse_candidates(case.entity_id, [item.fact for item in case.candidates])
            if fusion.conflict is not None:
                disposition = "CONFLICT"
                candidate_refs = fusion.conflict.candidate_references
                conflict_state = fusion.conflict.resolution_state.value
                conflict_states[conflict_state] += 1
                provenance_ok = set(candidate_refs) == expected_refs
                conflicts += 1
            else:
                assert fusion.canonical_fact is not None
                disposition = "CANONICAL"
                candidate_refs = fusion.canonical_fact.candidate_references
                provenance_ok = (
                    set(candidate_refs) == expected_refs
                    and set(candidate_refs).issubset(
                        set(fusion.canonical_fact.provenance.was_derived_from)
                    )
                )
                canonical += 1
                if len(sources) > 1:
                    corroborated += 1
        if disposition == "REVIEW":
            reviews += 1
        if provenance_ok is True:
            provenance_complete += 1
        correct = disposition == case.expected_disposition
        if not correct:
            incorrect += 1
        results.append(
            {
                "caseId": case.case_id,
                "attribute": case.attribute,
                "sources": sources,
                "candidateReferences": candidate_refs,
                "disposition": disposition,
                "conflictState": conflict_state,
                "expectedDisposition": case.expected_disposition,
                "correct": correct,
                "provenanceComplete": provenance_ok,
                "rationale": case.rationale,
            }
        )

    total = len(case_list)
    return {
        "schema": "podium7.multisource-validation-report.v1",
        "summary": {
            "cases": total,
            "canonicalCases": canonical,
            "corroboratedCases": corroborated,
            "conflictCases": conflicts,
            "conflictsByState": dict(sorted(conflict_states.items())),
            "reviewCases": reviews,
            "incorrectCases": incorrect,
            "provenanceApplicableCases": provenance_applicable,
            "provenanceCompleteCases": provenance_complete,
            "provenanceCompleteness": (
                None
                if provenance_applicable == 0
                else provenance_complete / provenance_applicable
            ),
            "corroborationRate": corroborated / total,
            "conflictRate": conflicts / total,
            "reviewRate": reviews / total,
            "sourceContribution": dict(sorted(source_contribution.items())),
            "resolverPolicyChanges": 0,
        },
        "results": results,
    }


__all__ = ["MultiSourceCase", "SourceCandidate", "evaluate_multisource_cases"]
