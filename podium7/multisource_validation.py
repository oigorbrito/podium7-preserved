from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .domain import CandidateFact
from .fusion import fuse_candidates


@dataclass(frozen=True)
class SourceCandidate:
    source_id: str
    fact: CandidateFact


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
        if not self.case_id or not self.entity_id or not self.attribute or not self.rationale:
            raise ValueError("case id, entity id, attribute, and rationale are required")
        if any(item.fact.attribute != self.attribute for item in self.candidates):
            raise ValueError("all candidate facts must match the case attribute")


def evaluate_multisource_cases(cases: Iterable[MultiSourceCase]) -> dict:
    case_list = tuple(cases)
    if not case_list:
        raise ValueError("at least one validation case is required")

    results = []
    source_contribution: dict[str, int] = {}
    corroborated = conflicts = reviews = canonical = provenance_complete = incorrect = 0

    for case in case_list:
        sources = tuple(sorted({item.source_id for item in case.candidates}))
        for source_id in sources:
            source_contribution[source_id] = source_contribution.get(source_id, 0) + 1

        if not case.candidates:
            disposition = "REVIEW"
            candidate_refs: tuple[str, ...] = ()
            provenance_ok = True
        else:
            fusion = fuse_candidates(case.entity_id, [item.fact for item in case.candidates])
            if fusion.conflict is not None:
                disposition = "CONFLICT"
                candidate_refs = fusion.conflict.candidate_references
                provenance_ok = True
                conflicts += 1
            else:
                assert fusion.canonical_fact is not None
                disposition = "CANONICAL"
                candidate_refs = fusion.canonical_fact.candidate_references
                provenance_ok = set(candidate_refs).issubset(set(fusion.canonical_fact.provenance.was_derived_from))
                canonical += 1
                if len(sources) > 1:
                    corroborated += 1
        if disposition == "REVIEW":
            reviews += 1
        if provenance_ok:
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
            "reviewCases": reviews,
            "incorrectCases": incorrect,
            "provenanceCompleteCases": provenance_complete,
            "provenanceCompleteness": provenance_complete / total,
            "corroborationRate": corroborated / total,
            "conflictRate": conflicts / total,
            "reviewRate": reviews / total,
            "sourceContribution": dict(sorted(source_contribution.items())),
            "resolverPolicyChanges": 0,
        },
        "results": results,
    }


__all__ = ["MultiSourceCase", "SourceCandidate", "evaluate_multisource_cases"]
