from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .catalog import CatalogStore
from .catalog_batch import CatalogBatchReport, ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_benchmark import load_catalog_identity_benchmark
from .catalog_quality import classify_review_reason
from .catalog_review import CatalogReviewQueue


def _present_vehicle_fields(vehicle: Mapping[str, Any]) -> tuple[str, ...]:
    fields: list[str] = []
    for field_name, value in vehicle.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)) and not value:
            continue
        fields.append(field_name)
    return tuple(fields)


def _unique_source_for_record(
    case: Mapping[str, Any],
    *,
    side: str,
    known_sources: set[str],
) -> str:
    case_id = case.get("id")
    vehicle = case.get(side)
    if not isinstance(vehicle, Mapping):
        raise ValueError(f"case {case_id!r} {side} vehicle must be an object")

    raw_field_sources = case.get("fieldSourceIds")
    if not isinstance(raw_field_sources, Mapping):
        raise ValueError(
            f"case {case_id!r} lacks explicit field-level source attribution for operational replay"
        )
    side_sources = raw_field_sources.get(side)
    if not isinstance(side_sources, Mapping):
        raise ValueError(
            f"case {case_id!r} lacks explicit field-level source attribution for {side}"
        )

    common_sources: set[str] | None = None
    for field_name in _present_vehicle_fields(vehicle):
        source_ids = side_sources.get(field_name)
        if (
            not isinstance(source_ids, list)
            or not source_ids
            or any(not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids)
        ):
            raise ValueError(
                f"case {case_id!r} {side}.{field_name} lacks explicit source attribution"
            )
        attributed = set(source_ids)
        unknown = attributed - known_sources
        if unknown:
            raise ValueError(
                f"case {case_id!r} {side}.{field_name} references unknown source ids"
            )
        common_sources = attributed if common_sources is None else common_sources & attributed

    if common_sources is None or len(common_sources) != 1:
        raise ValueError(
            f"case {case_id!r} {side} has no unique source common to every present field"
        )
    return next(iter(common_sources))


def build_source_backed_operational_records(paths: Iterable[str | Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path)
        load_catalog_identity_benchmark(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        version = payload["datasetVersion"]
        sources = {source["id"]: source for source in payload["sources"]}
        created_at = payload.get("createdAt", "2026-08-23")
        retrieved_at = f"{created_at}T00:00:00Z"
        known_sources = set(sources)

        for case in payload["cases"]:
            for side in ("left", "right"):
                source_id = _unique_source_for_record(case, side=side, known_sources=known_sources)
                source = sources[source_id]
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
