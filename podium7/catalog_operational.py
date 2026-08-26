from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import CatalogBatchReport, ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_review import CatalogReviewQueue
from .catalog_review_cause import CatalogReviewCauseStore, LEGACY_UNSNAPSHOTTED_CAUSE


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
            source_ids = case.get("sourceIds", ())
            if not source_ids:
                raise ValueError(f"case {case.get('id')!r} has no sourceIds")
            source = sources[source_ids[0]]
            for side in ("left", "right"):
                case_id = case["id"]
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
    store = CatalogStore()
    report = run_source_backed_operational_corpus(store, paths)
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
    cause_store = CatalogReviewCauseStore(store)
    tasks = review_queue.open_tasks(limit=100)
    cause_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    classifier_versions: Counter[str] = Counter()
    multiple_cause_tasks = 0
    unsnapshotted_tasks = 0

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
        for reason in reasons:
            reason_counts[reason] += 1

        snapshot = cause_store.get(task.id)
        if snapshot is None:
            unsnapshotted_tasks += 1
            cause_counts[LEGACY_UNSNAPSHOTTED_CAUSE] += 1
            continue

        classifier_versions[snapshot.classifier_version] += 1
        if len(snapshot.causes) > 1:
            multiple_cause_tasks += 1
        for cause in snapshot.causes:
            cause_counts[cause] += 1

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
            "unsnapshottedReviewTasks": unsnapshotted_tasks,
        },
        "actionsBySide": {
            side: dict(sorted(counter.items()))
            for side, counter in action_by_side.items()
        },
        "reviewCauses": dict(sorted(cause_counts.items())),
        "reviewReasons": dict(sorted(reason_counts.items())),
        "reviewCauseClassifierVersions": dict(sorted(classifier_versions.items())),
        "multipleCauseTasks": multiple_cause_tasks,
    }


__all__ = [
    "build_source_backed_operational_records",
    "measure_source_backed_operational_corpus",
    "run_source_backed_operational_corpus",
]
