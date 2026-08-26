from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, fields as dataclass_fields
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
IDENTITY_FIELD_NAMES = frozenset(item.name for item in dataclass_fields(CatalogVehicleIdentity))


@dataclass(frozen=True)
class CatalogBenchmarkCase:
    id: str
    expected: CatalogMatchOutcome
    left: CatalogVehicleIdentity
    right: CatalogVehicleIdentity
    source_ids: tuple[str, ...]
    rationale: str
    left_field_source_ids: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    right_field_source_ids: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


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


def _identity_field_is_present(identity: CatalogVehicleIdentity, field_name: str) -> bool:
    value = getattr(identity, field_name)
    if value is None:
        return False
    if isinstance(value, tuple) and not value:
        return False
    return True


def _parse_side_field_source_ids(
    raw: Any,
    *,
    side: str,
    identity: CatalogVehicleIdentity,
    case_source_ids: tuple[str, ...],
    case_id: str,
) -> dict[str, tuple[str, ...]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"case {case_id!r} fieldSourceIds.{side} must be an object")

    result: dict[str, tuple[str, ...]] = {}
    allowed_sources = set(case_source_ids)
    for field_name, raw_source_ids in raw.items():
        if field_name not in IDENTITY_FIELD_NAMES:
            raise ValueError(
                f"case {case_id!r} fieldSourceIds.{side} has unknown identity field {field_name!r}"
            )
        if not _identity_field_is_present(identity, field_name):
            raise ValueError(
                f"case {case_id!r} fieldSourceIds.{side}.{field_name} attributes an absent field"
            )
        if not isinstance(raw_source_ids, list) or not raw_source_ids:
            raise ValueError(
                f"case {case_id!r} fieldSourceIds.{side}.{field_name} requires a non-empty source list"
            )
        if any(not isinstance(source_id, str) or not source_id.strip() for source_id in raw_source_ids):
            raise ValueError(
                f"case {case_id!r} fieldSourceIds.{side}.{field_name} source ids must be non-empty strings"
            )
        if len(set(raw_source_ids)) != len(raw_source_ids):
            raise ValueError(
                f"case {case_id!r} fieldSourceIds.{side}.{field_name} source ids must be unique"
            )
        if any(source_id not in allowed_sources for source_id in raw_source_ids):
            raise ValueError(
                f"case {case_id!r} fieldSourceIds.{side}.{field_name} references a source outside case sourceIds"
            )
        result[field_name] = tuple(raw_source_ids)
    return result


def _parse_field_source_ids(
    raw: Any,
    *,
    left: CatalogVehicleIdentity,
    right: CatalogVehicleIdentity,
    case_source_ids: tuple[str, ...],
    case_id: str,
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    if raw is None:
        return {}, {}
    if not isinstance(raw, dict):
        raise ValueError(f"case {case_id!r} fieldSourceIds must be an object")
    unknown_sides = set(raw) - {"left", "right"}
    if unknown_sides:
        raise ValueError(f"case {case_id!r} fieldSourceIds has unknown side(s): {sorted(unknown_sides)!r}")
    return (
        _parse_side_field_source_ids(
            raw.get("left"),
            side="left",
            identity=left,
            case_source_ids=case_source_ids,
            case_id=case_id,
        ),
        _parse_side_field_source_ids(
            raw.get("right"),
            side="right",
            identity=right,
            case_source_ids=case_source_ids,
            case_id=case_id,
        ),
    )


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
        if len(set(case_source_ids)) != len(case_source_ids):
            raise ValueError(f"case {case_id!r} sourceIds must be unique")
        rationale = raw.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"case {case_id!r} requires a rationale")

        left = _identity_from_mapping(raw["left"])
        right = _identity_from_mapping(raw["right"])
        left_field_source_ids, right_field_source_ids = _parse_field_source_ids(
            raw.get("fieldSourceIds"),
            left=left,
            right=right,
            case_source_ids=case_source_ids,
            case_id=case_id,
        )

        cases.append(
            CatalogBenchmarkCase(
                id=case_id,
                expected=expected,
                left=left,
                right=right,
                source_ids=case_source_ids,
                rationale=rationale,
                left_field_source_ids=left_field_source_ids,
                right_field_source_ids=right_field_source_ids,
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
                "fieldSourceIds": {
                    "left": {field_name: list(source_ids) for field_name, source_ids in case.left_field_source_ids.items()},
                    "right": {field_name: list(source_ids) for field_name, source_ids in case.right_field_source_ids.items()},
                },
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
    "IDENTITY_FIELD_NAMES",
    "CatalogBenchmarkCase",
    "CatalogBenchmarkDataset",
    "evaluate_catalog_identity_benchmark",
    "load_catalog_identity_benchmark",
]
