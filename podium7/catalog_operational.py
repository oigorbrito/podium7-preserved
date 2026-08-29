from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import CatalogBatchReport, ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_quality import classify_review_reason
from .catalog_review import CatalogReviewQueue
from .operational_provenance import (
    measure_operational_provenance_eligibility,
    run_provenance_eligible_operational_corpus,
)


def build_source_backed_operational_records(paths: Iterable[str | Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "podium7.catalog-identity-golden.v1":
            raise ValueError(f"unsupported operational corpus source: {path}")
        version = payload.get("datasetVersion")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"datasetVersion is required: {path}")
        sources = {source["id"]: source for source in payload.get("sources", ())}
        if not sources:
            raise ValueError(f"source-backed dataset has no sources: {path}")
        created_at = payload.get("createdAt", "2026-08-23")
        retrieved_at = f"{created_at}T00:00:00Z"

        for case in payload.get("cases", ()):
            case_id = case.get("id")
            source_ids = case.get("sourceIds", ())
            if not source_ids:
                raise ValueError(f"case {case_id!r} has no sourceIds")
            if len(source_ids) != 1:
                raise ValueError(
                    f"case {case_id!r} has ambiguous case-level source attribution; "
                    "operational replay requires exactly one defensible source per record side"
                )
            source_id = source_ids[0]
            if source_id not in sources:
                raise ValueError(f"case {case_id!r} references unknown source {source_id!r}")
            source = sources[source_id]
            for side in ("left", "right"):
                evidence_id = f"operational:{version}:{case_id}:{side}"
                records.append(
                    {
                        "recordId": evidence_id,
                        "source": {
                            "id": source["id"],
                            "name": source.get("publisher") or source.get("title") or source["id"],
                            "locator": source["url"],
                        },
                        "evidence": {
                            "id": evidence_id,
                            "locator": source["url"],
                            "retrievedAt": retrieved_at,
                            "acquisitionMethod": "source-backed-golden-replay",
                            "rawContentRef": f"benchmark:{path.name}#{case_id}:{side}",
                        },
                        "vehicle": case[side],
                    }
                )
    if not records:
        raise ValueError("operational corpus requires at least one record")
    return records


def run_source_backed_operational_corpus(
    store: CatalogStore,
    paths: Iterable[str | Path],
) -> CatalogBatchReport:
    records = build_source_backed_operational_records(paths)
    return ingest_catalog_batch(store, parse_catalog_batch_payload({"records": records}))


def measure_source_backed_operational_corpus(paths: Iterable[str | Path]) -> dict[str, Any]:
    dataset_paths = tuple(Path(path) for path in paths)
    eligibility = measure_operational_provenance_eligibility(dataset_paths)
    store = CatalogStore()
    report = run_provenance_eligible_operational_corpus(store, dataset_paths)
    replayable_records = eligibility["summary"]["replayableRecords"]
    if report.total != replayable_records:
        raise RuntimeError("provenance eligibility and operational measurement record counts diverged")

    action_by_side: dict[str, Counter[str]] = {
        "left": Counter(),
        "right": Counter(),
    }
    for result in report.results:
        if result.record_id is None or result.action is None:
            continue
        side = result.record_id.rsplit(":", 1)[-1]
        if side in action_by_side:
            action_by_side[side][result.action.value] += 1

    review_queue = CatalogReviewQueue(store)
    tasks = review_queue.open_tasks(limit=100)
    cause_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    multiple_cause_tasks = 0
    for task in tasks:
        candidates = set(task.candidate_vehicle_ids)
        reasons = sorted(
            {
                comparison.reason
                for comparison in task.comparisons
                if comparison.vehicle_id in candidates
                and comparison.outcome in {"MATCH", "REVIEW"}
            }
        )
        if not reasons:
            cause_counts["UNKNOWN_REVIEW_CAUSE"] += 1
            continue
        categories = sorted({classify_review_reason(reason) for reason in reasons})
        for reason in reasons:
            reason_counts[reason] += 1
        if "UNKNOWN_REVIEW_CAUSE" in categories:
            cause_counts["UNKNOWN_REVIEW_CAUSE"] += 1
        elif len(categories) == 1:
            cause_counts[categories[0]] += 1
        else:
            multiple_cause_tasks += 1
            cause_counts["MULTIPLE_REVIEW_CAUSES"] += 1

    catalog_items = len(store.catalog_vehicle_ids_page(limit=100))
    return {
        "schema": "podium7.production-operational-measurement.v1",
        "summary": {
            "total": report.total,
            "created": report.created,
            "matched": report.matched,
            "review": report.review,
            "failed": report.failed,
            "automaticRate": (report.created + report.matched) / report.total,
            "reviewRate": report.review / report.total,
            "catalogItems": catalog_items,
            "openReviewTasks": len(tasks),
        },
        "provenanceEligibility": eligibility["summary"],
        "actionsBySide": {
            side: dict(sorted(counter.items()))
            for side, counter in action_by_side.items()
        },
        "reviewCauses": dict(sorted(cause_counts.items())),
        "reviewReasons": dict(sorted(reason_counts.items())),
        "multipleCauseTasks": multiple_cause_tasks,
    }


__all__ = [
    "build_source_backed_operational_records",
    "measure_source_backed_operational_corpus",
    "run_source_backed_operational_corpus",
]
