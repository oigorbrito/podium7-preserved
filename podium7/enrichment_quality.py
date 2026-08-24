from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_operational import build_source_backed_operational_records
from .catalog_quality import classify_review_reason, evaluate_identity_quality
from .catalog_review import CatalogReviewQueue
from .source_backed_enrichment import (
    apply_source_backed_overrides_to_records,
    evaluate_source_backed_enrichment,
    load_source_backed_enrichment_overrides,
)


def measure_enriched_operational_corpus(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
) -> dict[str, Any]:
    dataset_paths = tuple(paths)
    overrides = load_source_backed_enrichment_overrides(dataset_paths, enrichment_path)
    records = build_source_backed_operational_records(dataset_paths)
    records = apply_source_backed_overrides_to_records(records, overrides)

    store = CatalogStore()
    report = ingest_catalog_batch(store, parse_catalog_batch_payload({"records": records}))
    action_counts: Counter[str] = Counter()
    for result in report.results:
        if result.action is not None:
            action_counts[result.action.value] += 1

    tasks = CatalogReviewQueue(store).open_tasks(limit=100)
    causes: Counter[str] = Counter()
    reasons_by_evidence: dict[str, list[str]] = {}
    candidates_by_evidence: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        candidates = set(task.candidate_vehicle_ids)
        reasons = {
            comparison.reason
            for comparison in task.comparisons
            if comparison.vehicle_id in candidates
            and comparison.outcome in {"MATCH", "REVIEW"}
        }
        reasons_by_evidence[task.evidence_id] = sorted(reasons)
        candidate_details: list[dict[str, Any]] = []
        for vehicle_id in task.candidate_vehicle_ids:
            identity = store.get_catalog_vehicle(vehicle_id)
            comparison = next(
                (
                    item
                    for item in task.comparisons
                    if item.vehicle_id == vehicle_id
                ),
                None,
            )
            candidate_details.append(
                {
                    "vehicleId": vehicle_id,
                    "identity": None
                    if identity is None
                    else {
                        "make": identity.make,
                        "model": identity.model,
                        "generation": identity.generation,
                        "variant": identity.variant,
                        "powertrain": identity.powertrain,
                        "transmission": identity.transmission,
                        "bodyStyle": identity.body_style,
                        "market": identity.market,
                        "modelYearFrom": identity.model_year_from,
                        "modelYearTo": identity.model_year_to,
                    },
                    "outcome": None if comparison is None else comparison.outcome,
                    "reason": None if comparison is None else comparison.reason,
                }
            )
        candidates_by_evidence[task.evidence_id] = candidate_details

        if not reasons:
            causes["UNKNOWN_REVIEW_CAUSE"] += 1
            continue
        categories = {classify_review_reason(reason) for reason in reasons}
        if "UNKNOWN_REVIEW_CAUSE" in categories:
            causes["UNKNOWN_REVIEW_CAUSE"] += 1
        elif len(categories) == 1:
            causes[next(iter(categories))] += 1
        else:
            causes["MULTIPLE_REVIEW_CAUSES"] += 1

    return {
        "schema": "podium7.production-enriched-operational-measurement.v1",
        "summary": {
            "total": report.total,
            "created": report.created,
            "matched": report.matched,
            "review": report.review,
            "failed": report.failed,
            "openReviewTasks": len(tasks),
            "appliedEvidenceOverrides": len(overrides),
        },
        "actionCounts": dict(sorted(action_counts.items())),
        "reviewCauses": dict(sorted(causes.items())),
        "reviewReasonsByEvidence": dict(sorted(reasons_by_evidence.items())),
        "reviewCandidatesByEvidence": dict(sorted(candidates_by_evidence.items())),
    }


def evaluate_production_enrichment_quality_gate(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
) -> dict[str, Any]:
    dataset_paths = tuple(paths)
    identity_quality = evaluate_identity_quality(dataset_paths)
    enrichment = evaluate_source_backed_enrichment(dataset_paths, enrichment_path)
    operational = measure_enriched_operational_corpus(dataset_paths, enrichment_path)

    metrics = identity_quality["metrics"]
    summary = operational["summary"]
    review_causes = operational["reviewCauses"]
    checks = {
        "zeroIngestionFailures": summary["failed"] == 0,
        "sourceBackedReviewReduction": summary["review"] < 22,
        "noUnknownReviewCause": review_causes.get("UNKNOWN_REVIEW_CAUSE", 0) == 0,
        "identityPrecisionPreserved": metrics["autoMatchPrecision"] == 1.0,
        "identityRecallPreserved": metrics["autoMatchRecall"] == 1.0,
        "zeroFalseMergeRegression": metrics["falseMergeCount"] == 0,
        "zeroAmbiguousOvercommitRegression": metrics["ambiguousOvercommitCount"] == 0,
        "enrichmentObservationsCorrect": enrichment["summary"]["incorrect"] == 0,
        "zeroResolverPolicyChanges": enrichment["summary"]["resolverPolicyChanges"] == 0,
    }
    return {
        "schema": "podium7.production-enrichment-quality-gate.v1",
        "passed": all(checks.values()),
        "checks": checks,
        "operational": operational,
        "identityQuality": identity_quality,
        "enrichment": enrichment,
    }


__all__ = [
    "evaluate_production_enrichment_quality_gate",
    "measure_enriched_operational_corpus",
]
