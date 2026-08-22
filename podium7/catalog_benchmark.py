from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .catalog import (
    CatalogMatchOutcome,
    CatalogVehicleIdentity,
    ExternalIdentifier,
    ExternalIdentifierStrength,
    resolve_catalog_pair,
)


CATALOG_BENCHMARK_SCHEMA = "podium7.catalog-identity-golden.v1"


@dataclass(frozen=True)
class CatalogBenchmarkCase:
    id: str
    expected: CatalogMatchOutcome
    left: CatalogVehicleIdentity
    right: CatalogVehicleIdentity
    source_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class CatalogBenchmarkDataset:
    version: str
    source_ids: tuple[str, ...]
    cases: tuple[CatalogBenchmarkCase, ...]


def _identity_from_mapping(data: dict[str, Any]) -> CatalogVehicleIdentity:
    payload = dict(data)
    payload["aliases"] = tuple(payload.get("aliases", ()))
    payload["engine_identifiers"] = tuple(payload.get("engine_identifiers", ()))
    payload["external_identifiers"] = tuple(
        ExternalIdentifier(**item) for item in payload.get("external_identifiers", ())
    )
    return CatalogVehicleIdentity(**payload)


def load_catalog_identity_benchmark(path: str | Path) -> CatalogBenchmarkDataset:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != CATALOG_BENCHMARK_SCHEMA:
        raise ValueError("unsupported catalog benchmark schema")

    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("catalog benchmark datasetVersion is required")

    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("catalog benchmark sources are required")
    source_ids = tuple(source.get("id") for source in sources)
    if any(not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids):
        raise ValueError("catalog benchmark source ids must be non-empty strings")
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("catalog benchmark source ids must be unique")
    for source in sources:
        if not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            raise ValueError("catalog benchmark sources require https URLs")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("catalog benchmark cases are required")

    cases: list[CatalogBenchmarkCase] = []
    seen_case_ids: set[str] = set()
    known_sources = set(source_ids)
    for raw in raw_cases:
        case_id = raw.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("catalog benchmark case id is required")
        if case_id in seen_case_ids:
            raise ValueError(f"duplicate catalog benchmark case id {case_id!r}")
        seen_case_ids.add(case_id)

        expected = CatalogMatchOutcome(raw.get("expected"))
        case_source_ids = tuple(raw.get("sourceIds", ()))
        if not case_source_ids or any(source_id not in known_sources for source_id in case_source_ids):
            raise ValueError(f"case {case_id!r} has missing or unknown sourceIds")
        rationale = raw.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"case {case_id!r} requires a rationale")

        cases.append(
            CatalogBenchmarkCase(
                id=case_id,
                expected=expected,
                left=_identity_from_mapping(raw["left"]),
                right=_identity_from_mapping(raw["right"]),
                source_ids=case_source_ids,
                rationale=rationale,
            )
        )

    return CatalogBenchmarkDataset(
        version=version,
        source_ids=source_ids,
        cases=tuple(cases),
    )


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def evaluate_catalog_identity_benchmark(
    dataset: CatalogBenchmarkDataset,
    *,
    namespace_registry: dict[str, ExternalIdentifierStrength] | None = None,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for case in dataset.cases:
        decision = resolve_catalog_pair(
            case.left,
            case.right,
            namespace_registry=namespace_registry,
        )
        results.append(
            {
                "id": case.id,
                "expected": case.expected.value,
                "predicted": decision.outcome.value,
                "reason": decision.reason,
                "correct": decision.outcome is case.expected,
            }
        )

    total = len(results)
    expected_match = sum(result["expected"] == CatalogMatchOutcome.MATCH.value for result in results)
    expected_no_match = sum(result["expected"] == CatalogMatchOutcome.NO_MATCH.value for result in results)
    expected_review = sum(result["expected"] == CatalogMatchOutcome.REVIEW.value for result in results)
    predicted_match = sum(result["predicted"] == CatalogMatchOutcome.MATCH.value for result in results)
    predicted_review = sum(result["predicted"] == CatalogMatchOutcome.REVIEW.value for result in results)
    correct = sum(bool(result["correct"]) for result in results)

    true_match = sum(
        result["expected"] == CatalogMatchOutcome.MATCH.value
        and result["predicted"] == CatalogMatchOutcome.MATCH.value
        for result in results
    )
    false_merge = sum(
        result["expected"] == CatalogMatchOutcome.NO_MATCH.value
        and result["predicted"] == CatalogMatchOutcome.MATCH.value
        for result in results
    )
    missed_duplicate = sum(
        result["expected"] == CatalogMatchOutcome.MATCH.value
        and result["predicted"] == CatalogMatchOutcome.NO_MATCH.value
        for result in results
    )
    ambiguous_overcommit = sum(
        result["expected"] == CatalogMatchOutcome.REVIEW.value
        and result["predicted"] != CatalogMatchOutcome.REVIEW.value
        for result in results
    )

    return {
        "schema": "podium7.catalog-identity-benchmark-report.v1",
        "datasetVersion": dataset.version,
        "totalCases": total,
        "expected": {
            "MATCH": expected_match,
            "NO_MATCH": expected_no_match,
            "REVIEW": expected_review,
        },
        "predicted": {
            "MATCH": predicted_match,
            "NO_MATCH": total - predicted_match - predicted_review,
            "REVIEW": predicted_review,
        },
        "metrics": {
            "correct": correct,
            "accuracy": _rate(correct, total),
            "falseMergeCount": false_merge,
            "falseMergeRate": _rate(false_merge, expected_no_match),
            "missedDuplicateCount": missed_duplicate,
            "missedDuplicateRate": _rate(missed_duplicate, expected_match),
            "matchPrecision": _rate(true_match, predicted_match),
            "matchRecall": _rate(true_match, expected_match),
            "reviewRate": _rate(predicted_review, total),
            "ambiguousOvercommitCount": ambiguous_overcommit,
            "ambiguousOvercommitRate": _rate(ambiguous_overcommit, expected_review),
        },
        "cases": results,
    }


__all__ = [
    "CATALOG_BENCHMARK_SCHEMA",
    "CatalogBenchmarkCase",
    "CatalogBenchmarkDataset",
    "evaluate_catalog_identity_benchmark",
    "load_catalog_identity_benchmark",
]
