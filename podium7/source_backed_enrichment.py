from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogMatchOutcome, CatalogVehicleIdentity, resolve_catalog_pair
from .catalog_benchmark import CatalogBenchmarkCase, load_catalog_identity_benchmark


ENRICHMENT_SCHEMA = "podium7.source-backed-enrichment.v1"
_ALLOWED_SCALAR_FIELDS = {
    "generation",
    "variant",
    "powertrain",
    "transmission",
    "body_style",
    "market",
    "manufacture_year_from",
    "manufacture_year_to",
    "model_year_from",
    "model_year_to",
}


def _dataset_context(paths: Iterable[str | Path]) -> dict[tuple[str, str], dict[str, Any]]:
    context: dict[tuple[str, str], dict[str, Any]] = {}
    for raw_path in paths:
        path = Path(raw_path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        dataset = load_catalog_identity_benchmark(path)
        sources = {source["id"]: source["url"] for source in raw["sources"]}
        for case in dataset.cases:
            key = (dataset.version, case.id)
            if key in context:
                raise ValueError(f"duplicate benchmark case context {key!r}")
            context[key] = {
                "case": case,
                "sources": sources,
            }
    if not context:
        raise ValueError("at least one benchmark dataset is required")
    return context


def _apply_explicit_fields(
    identity: CatalogVehicleIdentity,
    field_values: dict[str, Any],
) -> CatalogVehicleIdentity:
    unknown = sorted(set(field_values) - (_ALLOWED_SCALAR_FIELDS | {"aliases"}))
    if unknown:
        raise ValueError("unsupported enrichment fields: " + ", ".join(unknown))

    updates: dict[str, Any] = {}
    for field, value in field_values.items():
        if field == "aliases":
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                raise ValueError("enrichment aliases must be a list of non-empty strings")
            merged = tuple(dict.fromkeys(identity.aliases + tuple(item.strip() for item in value)))
            if merged == identity.aliases:
                raise ValueError("enrichment aliases must add new explicit evidence")
            updates[field] = merged
            continue

        current = getattr(identity, field)
        if current is not None:
            raise ValueError(f"enrichment cannot overwrite existing field {field!r}")
        if field.endswith("_from") or field.endswith("_to"):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"enrichment field {field!r} must be an integer")
        elif not isinstance(value, str) or not value.strip():
            raise ValueError(f"enrichment field {field!r} must be non-empty text")
        updates[field] = value.strip() if isinstance(value, str) else value

    if not updates:
        return identity
    return replace(identity, **updates)


def _load_observations(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    context = _dataset_context(paths)
    payload = json.loads(Path(enrichment_path).read_text(encoding="utf-8"))
    if payload.get("schema") != ENRICHMENT_SCHEMA:
        raise ValueError("unsupported source-backed enrichment schema")
    observations = payload.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("source-backed enrichment observations are required")

    valid_outcomes = {item.value for item in CatalogMatchOutcome}
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for observation in observations:
        if not isinstance(observation, dict):
            raise ValueError("source-backed enrichment observation must be an object")
        observation_id = observation.get("id")
        version = observation.get("benchmarkDatasetVersion")
        case_id = observation.get("caseId")
        side = observation.get("side")
        source_id = observation.get("sourceId")
        effect = observation.get("evidenceEffect")
        field_values = observation.get("fieldValues")
        expected_before = observation.get("expectedBefore")
        expected_after = observation.get("expectedAfter")
        rationale = observation.get("rationale")

        if not isinstance(observation_id, str) or not observation_id.strip() or observation_id in seen:
            raise ValueError("enrichment observation ids must be unique non-empty strings")
        seen.add(observation_id)
        if not isinstance(version, str) or not isinstance(case_id, str):
            raise ValueError(f"observation {observation_id!r} requires benchmark version and case id")
        case_context = context.get((version, case_id))
        if case_context is None:
            raise ValueError(f"observation {observation_id!r} references an unknown benchmark case")
        case: CatalogBenchmarkCase = case_context["case"]
        if side not in {"left", "right"}:
            raise ValueError(f"observation {observation_id!r} side must be left or right")
        if source_id not in case.source_ids or source_id not in case_context["sources"]:
            raise ValueError(f"observation {observation_id!r} source is not declared by the benchmark case")
        if effect not in {"ADD_EXPLICIT_FIELD", "AMBIGUITY_CONFIRMED"}:
            raise ValueError(f"observation {observation_id!r} has unsupported evidence effect")
        if not isinstance(field_values, dict):
            raise ValueError(f"observation {observation_id!r} fieldValues must be an object")
        if effect == "ADD_EXPLICIT_FIELD" and not field_values:
            raise ValueError(f"observation {observation_id!r} explicit-field effect requires fieldValues")
        if effect == "AMBIGUITY_CONFIRMED" and field_values:
            raise ValueError(f"observation {observation_id!r} ambiguity confirmation cannot mutate identity")
        if expected_before not in valid_outcomes or expected_after not in valid_outcomes:
            raise ValueError(f"observation {observation_id!r} expected outcomes are invalid")
        if effect == "AMBIGUITY_CONFIRMED" and (
            expected_before != CatalogMatchOutcome.REVIEW.value
            or expected_after != CatalogMatchOutcome.REVIEW.value
        ):
            raise ValueError(
                f"observation {observation_id!r} ambiguity confirmation must preserve REVIEW"
            )
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"observation {observation_id!r} requires a rationale")

        target = case.left if side == "left" else case.right
        enriched = _apply_explicit_fields(target, field_values)
        validated.append(
            {
                **observation,
                "sourceLocator": case_context["sources"][source_id],
                "case": case,
                "enrichedIdentity": enriched,
            }
        )
    return validated, context


def load_source_backed_enrichment_overrides(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
) -> dict[str, dict[str, Any]]:
    observations, _ = _load_observations(paths, enrichment_path)
    overrides: dict[str, dict[str, Any]] = {}
    for observation in observations:
        if observation["evidenceEffect"] != "ADD_EXPLICIT_FIELD":
            continue
        evidence_id = (
            f"operational:{observation['benchmarkDatasetVersion']}:"
            f"{observation['caseId']}:{observation['side']}"
        )
        merged = overrides.setdefault(evidence_id, {})
        overlap = sorted(set(merged).intersection(observation["fieldValues"]))
        if overlap:
            raise ValueError(
                f"multiple explicit enrichment observations overlap for {evidence_id!r}: "
                + ", ".join(overlap)
            )
        merged.update(observation["fieldValues"])
    return overrides


def apply_source_backed_overrides_to_records(
    records: list[dict[str, Any]],
    overrides: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        record_copy = {
            **record,
            "source": dict(record["source"]),
            "evidence": dict(record["evidence"]),
            "vehicle": dict(record["vehicle"]),
        }
        evidence_id = record_copy["evidence"]["id"]
        field_values = overrides.get(evidence_id)
        if field_values is not None:
            vehicle = record_copy["vehicle"]
            for field, value in field_values.items():
                if field == "aliases":
                    existing = list(vehicle.get("aliases", ()))
                    vehicle["aliases"] = list(dict.fromkeys(existing + list(value)))
                else:
                    if vehicle.get(field) is not None:
                        raise ValueError(f"operational enrichment cannot overwrite {field!r} for {evidence_id!r}")
                    vehicle[field] = value
            seen.add(evidence_id)
        enriched.append(record_copy)
    return enriched


def evaluate_source_backed_enrichment(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
) -> dict[str, Any]:
    observations, _ = _load_observations(paths, enrichment_path)
    results: list[dict[str, Any]] = []
    for observation in observations:
        case: CatalogBenchmarkCase = observation["case"]
        before = resolve_catalog_pair(case.left, case.right)
        if observation["side"] == "left":
            left, right = observation["enrichedIdentity"], case.right
        else:
            left, right = case.left, observation["enrichedIdentity"]
        after = resolve_catalog_pair(left, right)
        results.append(
            {
                "id": observation["id"],
                "caseId": observation["caseId"],
                "sourceId": observation["sourceId"],
                "sourceLocator": observation["sourceLocator"],
                "evidenceEffect": observation["evidenceEffect"],
                "before": before.outcome.value,
                "beforeReason": before.reason,
                "after": after.outcome.value,
                "afterReason": after.reason,
                "expectedBefore": observation["expectedBefore"],
                "expectedAfter": observation["expectedAfter"],
                "correct": (
                    before.outcome.value == observation["expectedBefore"]
                    and after.outcome.value == observation["expectedAfter"]
                ),
                "resolverPolicyChange": False,
            }
        )

    resolved = sum(item["before"] == "REVIEW" and item["after"] == "MATCH" for item in results)
    retained = sum(item["after"] == "REVIEW" for item in results)
    incorrect = sum(not item["correct"] for item in results)
    return {
        "schema": "podium7.source-backed-enrichment-report.v1",
        "summary": {
            "observations": len(results),
            "resolvedReviews": resolved,
            "retainedReviews": retained,
            "incorrect": incorrect,
            "resolverPolicyChanges": 0,
        },
        "results": results,
    }


__all__ = [
    "ENRICHMENT_SCHEMA",
    "apply_source_backed_overrides_to_records",
    "evaluate_source_backed_enrichment",
    "load_source_backed_enrichment_overrides",
]
