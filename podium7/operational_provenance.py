from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from .catalog import CatalogStore
from .catalog_batch import CatalogBatchReport, ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_benchmark import load_catalog_identity_benchmark


BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION = "MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION"
BLOCK_MISSING_SIDE_FIELD_ATTRIBUTION = "MISSING_SIDE_FIELD_ATTRIBUTION"
BLOCK_MISSING_PRESENT_FIELD_ATTRIBUTION = "MISSING_PRESENT_FIELD_ATTRIBUTION"
BLOCK_NO_UNIQUE_COMMON_SOURCE = "NO_UNIQUE_COMMON_SOURCE"
BLOCK_INVALID_CASE_SOURCE_ATTRIBUTION = "INVALID_CASE_SOURCE_ATTRIBUTION"
BLOCK_UNKNOWN_CASE_SOURCE = "UNKNOWN_CASE_SOURCE"
BLOCK_INVALID_FIELD_ATTRIBUTION = "INVALID_FIELD_ATTRIBUTION"
BLOCK_UNKNOWN_FIELD_SOURCE = "UNKNOWN_FIELD_SOURCE"


class OperationalProvenanceBlock(ValueError):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


def _present_vehicle_fields(vehicle: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        field_name
        for field_name, value in vehicle.items()
        if value is not None and not (isinstance(value, (list, tuple)) and not value)
    )


def unique_source_for_record(
    case: Mapping[str, Any],
    *,
    side: str,
    known_sources: set[str],
) -> tuple[str, str]:
    case_id = case.get("id")
    vehicle = case.get(side)
    if not isinstance(vehicle, Mapping):
        raise ValueError(f"case {case_id!r} {side} vehicle must be an object")

    raw_field_sources = case.get("fieldSourceIds")
    case_sources = case.get("sourceIds")
    if not isinstance(case_sources, list) or not case_sources:
        raise OperationalProvenanceBlock(
            BLOCK_INVALID_CASE_SOURCE_ATTRIBUTION,
            f"case {case_id!r} has invalid case-level source attribution",
        )
    if any(not isinstance(source_id, str) or not source_id.strip() for source_id in case_sources):
        raise OperationalProvenanceBlock(
            BLOCK_INVALID_CASE_SOURCE_ATTRIBUTION,
            f"case {case_id!r} has invalid case-level source attribution",
        )
    if len(set(case_sources)) != len(case_sources):
        raise OperationalProvenanceBlock(
            BLOCK_INVALID_CASE_SOURCE_ATTRIBUTION,
            f"case {case_id!r} has duplicate case-level source attribution",
        )
    if set(case_sources) - known_sources:
        raise OperationalProvenanceBlock(
            BLOCK_UNKNOWN_CASE_SOURCE,
            f"case {case_id!r} references unknown source ids",
        )

    if raw_field_sources is None:
        if len(case_sources) == 1:
            return case_sources[0], "SOLE_CASE_SOURCE"
        raise OperationalProvenanceBlock(
            BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION,
            f"case {case_id!r} has multiple sourceIds and lacks explicit field-level source attribution for operational replay",
        )
    if not isinstance(raw_field_sources, Mapping):
        raise OperationalProvenanceBlock(
            BLOCK_INVALID_FIELD_ATTRIBUTION,
            f"case {case_id!r} fieldSourceIds must be an object when provided",
        )
    side_sources = raw_field_sources.get(side)
    if not isinstance(side_sources, Mapping):
        raise OperationalProvenanceBlock(
            BLOCK_MISSING_SIDE_FIELD_ATTRIBUTION,
            f"case {case_id!r} lacks explicit field-level source attribution for {side}",
        )

    common_sources: set[str] | None = None
    for field_name in _present_vehicle_fields(vehicle):
        source_ids = side_sources.get(field_name)
        if not isinstance(source_ids, list) or not source_ids:
            raise OperationalProvenanceBlock(
                BLOCK_MISSING_PRESENT_FIELD_ATTRIBUTION,
                f"case {case_id!r} {side}.{field_name} lacks explicit source attribution",
            )
        if any(not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids):
            raise OperationalProvenanceBlock(
                BLOCK_INVALID_FIELD_ATTRIBUTION,
                f"case {case_id!r} {side}.{field_name} has invalid source attribution",
            )
        if len(set(source_ids)) != len(source_ids):
            raise OperationalProvenanceBlock(
                BLOCK_INVALID_FIELD_ATTRIBUTION,
                f"case {case_id!r} {side}.{field_name} source attribution contains duplicates",
            )
        attributed = set(source_ids)
        if attributed - known_sources:
            raise OperationalProvenanceBlock(
                BLOCK_UNKNOWN_FIELD_SOURCE,
                f"case {case_id!r} {side}.{field_name} references unknown source ids",
            )
        common_sources = attributed if common_sources is None else common_sources & attributed

    if common_sources is None or len(common_sources) != 1:
        raise OperationalProvenanceBlock(
            BLOCK_NO_UNIQUE_COMMON_SOURCE,
            f"case {case_id!r} {side} has no unique source common to every present field",
        )
    return next(iter(common_sources)), "EXPLICIT_FIELD_ATTRIBUTION"


def measure_operational_provenance_eligibility(paths: Iterable[str | Path]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    dataset_versions: list[str] = []
    case_ids: set[str] = set()

    for raw_path in paths:
        path = Path(raw_path)
        load_catalog_identity_benchmark(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        version = payload["datasetVersion"]
        dataset_versions.append(version)
        known_sources = {source["id"] for source in payload["sources"]}

        for case in payload["cases"]:
            case_id = case["id"]
            case_ids.add(f"{version}:{case_id}")
            for side in ("left", "right"):
                try:
                    source_id, method = unique_source_for_record(
                        case,
                        side=side,
                        known_sources=known_sources,
                    )
                except OperationalProvenanceBlock as exc:
                    records.append({
                        "datasetVersion": version,
                        "caseId": case_id,
                        "side": side,
                        "replayable": False,
                        "method": None,
                        "sourceId": None,
                        "reasonCode": exc.reason_code,
                        "reason": str(exc),
                    })
                else:
                    records.append({
                        "datasetVersion": version,
                        "caseId": case_id,
                        "side": side,
                        "replayable": True,
                        "method": method,
                        "sourceId": source_id,
                        "reasonCode": None,
                        "reason": None,
                    })

    if not records:
        raise ValueError("operational provenance eligibility requires at least one record")

    replayable = [record for record in records if record["replayable"]]
    blocked = [record for record in records if not record["replayable"]]
    return {
        "schema": "podium7.operational-provenance-eligibility.v1",
        "datasets": dataset_versions,
        "summary": {
            "cases": len(case_ids),
            "records": len(records),
            "replayableRecords": len(replayable),
            "blockedRecords": len(blocked),
            "replayableRate": len(replayable) / len(records),
            "replayableByMethod": dict(sorted(Counter(record["method"] for record in replayable).items())),
            "blockedByReasonCode": dict(sorted(Counter(record["reasonCode"] for record in blocked).items())),
            "blockedByReason": dict(sorted(Counter(record["reason"] for record in blocked).items())),
        },
        "records": records,
    }


def build_provenance_eligible_operational_records(
    paths: Iterable[str | Path],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path)
        load_catalog_identity_benchmark(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        version = payload["datasetVersion"]
        sources = {source["id"]: source for source in payload["sources"]}
        known_sources = set(sources)
        created_at = payload.get("createdAt", "2026-08-23")
        retrieved_at = f"{created_at}T00:00:00Z"

        for case in payload["cases"]:
            case_id = case["id"]
            for side in ("left", "right"):
                try:
                    source_id, _method = unique_source_for_record(
                        case,
                        side=side,
                        known_sources=known_sources,
                    )
                except OperationalProvenanceBlock:
                    continue
                source = sources[source_id]
                evidence_id = f"operational:{version}:{case_id}:{side}"
                records.append({
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
                })
    if not records:
        raise ValueError("provenance-eligible operational corpus requires at least one record")
    return records


def run_provenance_eligible_operational_corpus(
    store: CatalogStore,
    paths: Iterable[str | Path],
) -> CatalogBatchReport:
    records = build_provenance_eligible_operational_records(paths)
    return ingest_catalog_batch(store, parse_catalog_batch_payload({"records": records}))


__all__ = [
    "BLOCK_INVALID_CASE_SOURCE_ATTRIBUTION",
    "BLOCK_INVALID_FIELD_ATTRIBUTION",
    "BLOCK_MISSING_PRESENT_FIELD_ATTRIBUTION",
    "BLOCK_MISSING_SIDE_FIELD_ATTRIBUTION",
    "BLOCK_NO_UNIQUE_COMMON_SOURCE",
    "BLOCK_UNKNOWN_CASE_SOURCE",
    "BLOCK_UNKNOWN_FIELD_SOURCE",
    "BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION",
    "OperationalProvenanceBlock",
    "build_provenance_eligible_operational_records",
    "measure_operational_provenance_eligibility",
    "run_provenance_eligible_operational_corpus",
    "unique_source_for_record",
]
