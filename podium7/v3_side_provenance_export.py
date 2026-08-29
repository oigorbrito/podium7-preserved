from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

V3_SIDE_PROVENANCE_EXPORT_SCHEMA = "podium7.v3-side-provenance-export.v1"
V3_SIDE_PROVENANCE_EXPORT_VERSION = "1.0"
_BENCHMARK_SCHEMA = "podium7.catalog-identity-golden.v1"
_DEFAULT_DATASETS = (
    Path("benchmarks") / "catalog_identity_golden_v1.json",
    Path("benchmarks") / "catalog_identity_golden_br_v1.json",
    Path("benchmarks") / "catalog_identity_br_adjacent_incomplete_v1.json",
    Path("benchmarks") / "catalog_identity_year_semantics_challenge_v1.json",
)
_DEFAULT_ENRICHMENT = Path("benchmarks") / "source_backed_enrichment_v3.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_benchmark_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != _BENCHMARK_SCHEMA:
        raise ValueError(f"unsupported benchmark schema: {path}")
    return payload


def _non_empty_fields(side: dict[str, Any]) -> list[str]:
    fields = []
    for key, value in side.items():
        if value is None:
            continue
        if key == "aliases" and not value:
            continue
        fields.append(key)
    return sorted(fields)


def _field_value(side: dict[str, Any], field: str) -> Any:
    return side.get(field)


def _load_explicit_bindings(
    dataset_paths: Iterable[str | Path],
    enrichment_path: str | Path,
) -> dict[tuple[str, str, str, str], list[dict[str, Any]]]:
    payload = json.loads(Path(enrichment_path).read_text(encoding="utf-8"))
    if payload.get("schema") != "podium7.source-backed-enrichment.v1":
        raise ValueError("unsupported source-backed enrichment schema")
    observations = payload.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("source-backed enrichment observations are required")

    versions = { _load_benchmark_payload(Path(path))["datasetVersion"] for path in dataset_paths }
    explicit: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for observation in observations:
        if observation.get("evidenceEffect") != "ADD_EXPLICIT_FIELD":
            continue
        version = observation.get("benchmarkDatasetVersion")
        case_id = observation.get("caseId")
        side = observation.get("side")
        source_id = observation.get("sourceId")
        field_values = observation.get("fieldValues")
        if version not in versions:
            continue
        if not isinstance(field_values, dict) or not isinstance(case_id, str) or not isinstance(side, str):
            raise ValueError("invalid enrichment observation payload")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("invalid enrichment observation source id")
        key = (version, case_id, side)
        for field_name, value in field_values.items():
            explicit.setdefault(key + (field_name,), []).append(
                {
                    "observationId": observation["id"],
                    "sourceId": source_id,
                    "rawEvidenceRef": f"enrichment:{version}:{case_id}:{side}",
                    "fieldValue": value,
                }
            )
    return explicit


def _binding_status(bindings: list[dict[str, Any]]) -> str:
    if not bindings:
        return "NO_EXPLICIT_BINDING"
    source_ids = {item["sourceId"] for item in bindings}
    if any("rawEvidenceRef" not in item for item in bindings):
        return "MISSING_EVIDENCE_REFERENCE"
    if len(source_ids) > 1:
        return "MULTIPLE_EXPLICIT_SOURCES"
    values = {json.dumps(item["fieldValue"], sort_keys=True, ensure_ascii=False) for item in bindings}
    if len(values) > 1:
        return "CONTRADICTORY"
    return "EXPLICIT"


def build_v3_side_provenance_export(
    dataset_paths: Iterable[str | Path] = _DEFAULT_DATASETS,
    enrichment_path: str | Path = _DEFAULT_ENRICHMENT,
) -> dict[str, Any]:
    dataset_paths = tuple(Path(path) for path in dataset_paths)
    if not dataset_paths:
        raise ValueError("at least one dataset is required")

    benchmark_payloads = [_load_benchmark_payload(path) for path in dataset_paths]
    cases: list[dict[str, Any]] = []
    dataset_fingerprints = []
    for path, payload in zip(dataset_paths, benchmark_payloads, strict=True):
        dataset_fingerprints.append(
            {
                "path": str(path),
                "datasetVersion": payload["datasetVersion"],
                "sha256": _sha256(path),
                "sourceIds": [source["id"] for source in payload["sources"]],
                "caseCount": len(payload["cases"]),
            }
        )
        for case in payload["cases"]:
            cases.append({**case, "datasetVersion": payload["datasetVersion"]})

    explicit_bindings = _load_explicit_bindings(dataset_paths, enrichment_path)
    blocked_sides: list[dict[str, Any]] = []
    classification_counts = {
        "EXPLICITLY_RECONSTRUCTABLE": 0,
        "AMBIGUOUS_MULTI_SOURCE": 0,
        "MISSING_RETAINED_EVIDENCE": 0,
        "CONTRADICTORY_EVIDENCE": 0,
        "OTHER_BLOCKED": 0,
    }

    replayable_case_count = 0
    blocked_case_count = 0
    for payload, path in zip(benchmark_payloads, dataset_paths, strict=True):
        version = payload["datasetVersion"]
        for case in payload["cases"]:
            if len(case["sourceIds"]) == 1:
                replayable_case_count += 1
                continue
            blocked_case_count += 1
            for side_name in ("left", "right"):
                side = case[side_name]
                present_fields = _non_empty_fields(side)
                field_bindings = []
                explicit_sources: set[str] = set()
                contradictory = False
                missing_ref = False
                multiple_source = False
                for field in present_fields:
                    bindings = explicit_bindings.get((version, case["id"], side_name, field), [])
                    status = _binding_status(bindings)
                    if status == "EXPLICIT":
                        explicit_sources.update(item["sourceId"] for item in bindings)
                    elif status == "MULTIPLE_EXPLICIT_SOURCES":
                        multiple_source = True
                    elif status == "CONTRADICTORY":
                        contradictory = True
                    elif status == "MISSING_EVIDENCE_REFERENCE":
                        missing_ref = True
                    field_bindings.append(
                        {
                            "fieldName": field,
                            "candidateRefs": [item["observationId"] for item in bindings],
                            "sourceIds": sorted({item["sourceId"] for item in bindings}),
                            "rawEvidenceRefs": sorted({item["rawEvidenceRef"] for item in bindings}),
                            "bindingStatus": status,
                        }
                    )
                if all(binding["bindingStatus"] == "EXPLICIT" for binding in field_bindings) and len(explicit_sources) == 1:
                    classification = "EXPLICITLY_RECONSTRUCTABLE"
                elif contradictory:
                    classification = "CONTRADICTORY_EVIDENCE"
                elif multiple_source:
                    classification = "AMBIGUOUS_MULTI_SOURCE"
                elif missing_ref:
                    classification = "MISSING_RETAINED_EVIDENCE"
                else:
                    classification = "OTHER_BLOCKED"
                classification_counts[classification] += 1
                blocked_sides.append(
                    {
                        "caseId": case["id"],
                        "side": side_name,
                        "presentFields": present_fields,
                        "declaredSourceIds": list(case["sourceIds"]),
                        "fieldBindings": field_bindings,
                        "classification": classification,
                    }
                )

    total_cases = len(cases)
    total_sides = total_cases * 2
    replayable_sides = replayable_case_count * 2
    blocked_sides_count = blocked_case_count * 2
    if total_cases != 36 or total_sides != 72 or replayable_sides != 12 or blocked_sides_count != 60:
        raise ValueError(
            "V3 side provenance export fail-closed: unexpected universe "
            f"cases={total_cases} sides={total_sides} replayable={replayable_sides} blocked={blocked_sides_count}"
        )

    return {
        "schema": V3_SIDE_PROVENANCE_EXPORT_SCHEMA,
        "version": V3_SIDE_PROVENANCE_EXPORT_VERSION,
        "dataset": {
            "identity": "v3-side-provenance-export",
            "version": "1.0",
            "hash": hashlib.sha256(
                json.dumps(dataset_fingerprints, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest(),
            "inputs": dataset_fingerprints,
            "enrichment": {
                "path": str(Path(enrichment_path)),
                "sha256": _sha256(Path(enrichment_path)),
            },
        },
        "counts": {
            "totalCases": total_cases,
            "totalSides": total_sides,
            "replayableSides": replayable_sides,
            "blockedSides": blocked_sides_count,
        },
        "blockedSides": blocked_sides,
        "classificationCounts": classification_counts,
    }


def export_v3_side_provenance_json(
    dataset_paths: Iterable[str | Path] = _DEFAULT_DATASETS,
    enrichment_path: str | Path = _DEFAULT_ENRICHMENT,
    *,
    indent: int | None = 2,
) -> str:
    return json.dumps(
        build_v3_side_provenance_export(dataset_paths, enrichment_path),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        indent=indent,
    )


__all__ = [
    "V3_SIDE_PROVENANCE_EXPORT_SCHEMA",
    "V3_SIDE_PROVENANCE_EXPORT_VERSION",
    "build_v3_side_provenance_export",
    "export_v3_side_provenance_json",
]
