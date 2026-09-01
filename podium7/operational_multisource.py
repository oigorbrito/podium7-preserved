from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .catalog import CatalogStore
from .catalog_benchmark import load_catalog_identity_benchmark
from .catalog_multisource_ingestion import (
    CatalogMultisourceIngestionResult,
    ingest_catalog_multisource_v2,
)
from .catalog_multisource_v2 import parse_catalog_multisource_v2_record
from .operational_provenance import measure_operational_provenance_eligibility


MULTISOURCE_FIELD_ATTRIBUTION_SCHEMA = "podium7.catalog-operational-field-attribution.v1"
MULTISOURCE_REPLAY_METHOD = "MULTISOURCE_FIELD_ATTRIBUTION_V2"


def _present_fields(vehicle: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        field
        for field, value in vehicle.items()
        if value is not None and not (isinstance(value, (list, tuple)) and not value)
    )


def _load_overlay(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != MULTISOURCE_FIELD_ATTRIBUTION_SCHEMA:
        raise ValueError("unsupported multisource field-attribution schema")
    mappings = payload.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        raise ValueError("multisource field attribution requires at least one mapping")
    return payload


def _benchmark_payload(path: Path) -> dict[str, Any]:
    load_catalog_identity_benchmark(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _mapping_key(mapping: Mapping[str, Any]) -> tuple[str, str, str]:
    dataset_version = mapping.get("benchmarkDatasetVersion")
    case_id = mapping.get("caseId")
    side = mapping.get("side")
    if not isinstance(dataset_version, str) or not dataset_version.strip():
        raise ValueError("mapping benchmarkDatasetVersion is required")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("mapping caseId is required")
    if side not in {"left", "right"}:
        raise ValueError("mapping side must be left or right")
    return dataset_version, case_id, side


def build_multisource_operational_records(
    benchmark_paths: Iterable[str | Path],
    attribution_path: str | Path,
) -> list[dict[str, Any]]:
    paths = [Path(path) for path in benchmark_paths]
    by_name = {path.name: path for path in paths}
    if len(by_name) != len(paths):
        raise ValueError("benchmark filenames must be unique")

    overlay = _load_overlay(attribution_path)
    records: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for mapping in overlay["mappings"]:
        if not isinstance(mapping, Mapping):
            raise ValueError("multisource attribution mapping must be an object")
        key = _mapping_key(mapping)
        if key in seen_keys:
            raise ValueError("duplicate multisource attribution mapping")
        seen_keys.add(key)

        benchmark_name = mapping.get("benchmark")
        if benchmark_name not in by_name:
            raise ValueError(f"mapping benchmark is not in active scope: {benchmark_name!r}")
        benchmark_path = by_name[benchmark_name]
        benchmark = _benchmark_payload(benchmark_path)
        dataset_version, case_id, side = key
        if benchmark.get("datasetVersion") != dataset_version:
            raise ValueError("mapping benchmarkDatasetVersion does not match benchmark")

        cases = [case for case in benchmark["cases"] if case.get("id") == case_id]
        if len(cases) != 1:
            raise ValueError(f"mapping case must resolve exactly once: {case_id!r}")
        case = cases[0]
        vehicle = case.get(side)
        if not isinstance(vehicle, Mapping):
            raise ValueError("mapping side vehicle must be an object")

        case_source_ids = case.get("sourceIds")
        if not isinstance(case_source_ids, list) or not case_source_ids:
            raise ValueError("mapping case must declare sourceIds")
        if len(set(case_source_ids)) != len(case_source_ids):
            raise ValueError("mapping case sourceIds must be unique")

        sources = {source["id"]: source for source in benchmark["sources"]}
        if set(case_source_ids) - set(sources):
            raise ValueError("mapping case references unknown sourceIds")

        field_sources = mapping.get("fieldSourceIds")
        if not isinstance(field_sources, Mapping):
            raise ValueError("mapping fieldSourceIds must be an object")
        present_fields = set(_present_fields(vehicle))
        if set(field_sources) != present_fields:
            missing = sorted(present_fields - set(field_sources))
            extra = sorted(set(field_sources) - present_fields)
            raise ValueError(
                f"mapping must cover exactly present fields; missing={missing}, extra={extra}"
            )

        normalized_field_sources: dict[str, tuple[str, ...]] = {}
        used_source_ids: set[str] = set()
        for field in sorted(present_fields):
            raw_ids = field_sources[field]
            if (
                isinstance(raw_ids, (str, bytes))
                or not isinstance(raw_ids, Sequence)
                or not raw_ids
            ):
                raise ValueError(f"mapping {field} must reference at least one source")
            source_ids = tuple(raw_ids)
            if any(not isinstance(source_id, str) or not source_id.strip() for source_id in source_ids):
                raise ValueError(f"mapping {field} contains invalid source id")
            if len(set(source_ids)) != len(source_ids):
                raise ValueError(f"mapping {field} contains duplicate source id")
            if set(source_ids) - set(case_source_ids):
                raise ValueError(f"mapping {field} references source outside case sourceIds")
            normalized_field_sources[field] = tuple(sorted(source_ids))
            used_source_ids.update(source_ids)

        if len(used_source_ids) < 2:
            raise ValueError("multisource overlay must require at least two sources")
        common = set.intersection(
            *(set(source_ids) for source_ids in normalized_field_sources.values())
        )
        if common:
            raise ValueError("multisource overlay must not have a source common to every field")

        retrieved_at = f"{benchmark.get('createdAt', '2026-09-01')}T00:00:00Z"
        evidence_id_by_source = {
            source_id: f"operational-v2:{dataset_version}:{case_id}:{side}:{source_id}"
            for source_id in sorted(used_source_ids)
        }
        operational_payload = {
            "contractVersion": "podium7.catalog-operational.v2",
            "recordId": f"operational-v2:{dataset_version}:{case_id}:{side}",
            "vehicle": dict(vehicle),
            "provenance": {
                "sources": [
                    {
                        "id": source_id,
                        "name": sources[source_id].get("publisher")
                        or sources[source_id].get("title")
                        or source_id,
                        "locator": sources[source_id]["url"],
                    }
                    for source_id in sorted(used_source_ids)
                ],
                "evidence": [
                    {
                        "id": evidence_id_by_source[source_id],
                        "sourceId": source_id,
                        "locator": sources[source_id]["url"],
                        "retrievedAt": retrieved_at,
                        "acquisitionMethod": "source-backed-golden-replay-v2",
                        "rawContentRef": (
                            f"benchmark:{benchmark_path.name}#{case_id}:{side}:{source_id}"
                        ),
                    }
                    for source_id in sorted(used_source_ids)
                ],
                "fieldEvidence": {
                    field: [evidence_id_by_source[source_id] for source_id in source_ids]
                    for field, source_ids in normalized_field_sources.items()
                },
            },
        }
        parse_catalog_multisource_v2_record(operational_payload)
        records.append(
            {
                "benchmark": benchmark_path.name,
                "datasetVersion": dataset_version,
                "caseId": case_id,
                "side": side,
                "sourceIds": tuple(sorted(used_source_ids)),
                "payload": operational_payload,
            }
        )

    return records


def measure_combined_operational_provenance_eligibility(
    benchmark_paths: Iterable[str | Path],
    attribution_path: str | Path,
) -> dict[str, Any]:
    paths = [Path(path) for path in benchmark_paths]
    base = measure_operational_provenance_eligibility(paths)
    records = deepcopy(base["records"])
    overlays = build_multisource_operational_records(paths, attribution_path)

    for overlay in overlays:
        matches = [
            record
            for record in records
            if record["datasetVersion"] == overlay["datasetVersion"]
            and record["caseId"] == overlay["caseId"]
            and record["side"] == overlay["side"]
        ]
        if len(matches) != 1:
            raise ValueError("overlay target must resolve exactly once in base measurement")
        record = matches[0]
        if record["replayable"]:
            raise ValueError("multisource overlay must target a currently blocked record")
        record.update(
            {
                "replayable": True,
                "method": MULTISOURCE_REPLAY_METHOD,
                "sourceId": None,
                "sourceIds": list(overlay["sourceIds"]),
                "reasonCode": None,
                "reason": None,
            }
        )

    replayable = [record for record in records if record["replayable"]]
    blocked = [record for record in records if not record["replayable"]]
    return {
        "schema": "podium7.operational-provenance-eligibility.combined-v2",
        "datasets": base["datasets"],
        "summary": {
            "cases": base["summary"]["cases"],
            "records": len(records),
            "replayableRecords": len(replayable),
            "blockedRecords": len(blocked),
            "replayableRate": len(replayable) / len(records),
            "replayableByMethod": dict(
                sorted(Counter(record["method"] for record in replayable).items())
            ),
            "blockedByReasonCode": dict(
                sorted(Counter(record["reasonCode"] for record in blocked).items())
            ),
        },
        "records": records,
    }


def run_multisource_operational_records(
    store: CatalogStore,
    records: Sequence[Mapping[str, Any]],
) -> tuple[CatalogMultisourceIngestionResult, ...]:
    results: list[CatalogMultisourceIngestionResult] = []
    for record in records:
        payload = record.get("payload")
        results.append(
            ingest_catalog_multisource_v2(
                store,
                parse_catalog_multisource_v2_record(payload),
            )
        )
    return tuple(results)


__all__ = [
    "MULTISOURCE_FIELD_ATTRIBUTION_SCHEMA",
    "MULTISOURCE_REPLAY_METHOD",
    "build_multisource_operational_records",
    "measure_combined_operational_provenance_eligibility",
    "run_multisource_operational_records",
]
