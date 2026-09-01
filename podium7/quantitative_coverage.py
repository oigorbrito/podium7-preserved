from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any

from podium7.enrichment_contract import CONTRACT_FIELDS


COVERAGE_SCHEMA = "podium7.quantitative-coverage-benchmark.v1"
RESULT_SCHEMA = "podium7.quantitative-coverage-result.v1"
_ALLOWED_STATES = {"known", "unknown", "not_applicable"}
_ALLOWED_SHAPES = {"scalar", "range", "limit", "multiple"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def load_coverage_fixture(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != COVERAGE_SCHEMA:
        raise ValueError("unsupported quantitative coverage fixture schema")
    _text(payload.get("corpusVersion"), "corpusVersion")
    source = payload.get("source")
    if not isinstance(source, dict):
        raise ValueError("source must be an object")
    _text(source.get("family"), "source.family")
    _text(source.get("provenanceRef"), "source.provenanceRef")
    if source.get("market") != "BR":
        raise ValueError("Brazil coverage fixture source.market must be BR")

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw in records:
        if not isinstance(raw, dict):
            raise ValueError("record must be an object")
        vehicle_id = _text(raw.get("vehicleId"), "vehicleId")
        field = _text(raw.get("field"), "field")
        if field not in CONTRACT_FIELDS:
            raise ValueError(f"unsupported quantitative field {field!r}")
        key = (vehicle_id, field)
        if key in seen:
            raise ValueError(f"duplicate vehicle/field record: {vehicle_id} {field}")
        seen.add(key)
        state = raw.get("knowledgeState")
        if state not in _ALLOWED_STATES:
            raise ValueError("unsupported knowledgeState")
        publication_eligible = raw.get("publicationEligible")
        if not isinstance(publication_eligible, bool):
            raise ValueError("publicationEligible must be boolean")
        provenance_ref = _text(raw.get("provenanceRef"), "provenanceRef")
        reason = raw.get("reason")
        if reason is not None:
            reason = _text(reason, "reason")

        value_shape = raw.get("valueShape")
        value = raw.get("value")
        unit = raw.get("unit")
        context = raw.get("context") or {}
        if not isinstance(context, dict):
            raise ValueError("context must be an object")
        clean_context: dict[str, str] = {}
        for name in ("market", "applicability", "methodology"):
            if context.get(name) is not None:
                clean_context[name] = _text(context[name], f"context.{name}")

        conflict = raw.get("conflict")
        if conflict is not None:
            if not isinstance(conflict, dict):
                raise ValueError("conflict must be an object")
            refs = conflict.get("provenanceRefs")
            if not isinstance(refs, list) or len(refs) < 2:
                raise ValueError("conflict requires at least two provenanceRefs")
            conflict = {
                "provenanceRefs": sorted(_text(ref, "conflict provenanceRef") for ref in refs),
                "reason": _text(conflict.get("reason"), "conflict.reason"),
            }
            if publication_eligible:
                raise ValueError("unresolved conflict cannot be publication eligible")

        if state == "known":
            if value_shape not in _ALLOWED_SHAPES:
                raise ValueError("known record requires supported valueShape")
            if value is None or not isinstance(unit, str) or not unit.strip():
                raise ValueError("known record requires value and unit")
            if not publication_eligible and reason is None:
                raise ValueError("known non-publishable record requires reason")
        else:
            if value_shape is not None or value is not None or unit is not None:
                raise ValueError("unknown/not_applicable record cannot carry value, shape, or unit")
            if publication_eligible:
                raise ValueError("unknown/not_applicable record cannot be publication eligible")
            if reason is None:
                raise ValueError("unknown/not_applicable record requires deterministic reason")

        normalized.append(
            {
                "vehicleId": vehicle_id,
                "field": field,
                "knowledgeState": state,
                "valueShape": value_shape,
                "value": value,
                "unit": unit.strip() if isinstance(unit, str) else None,
                "context": clean_context,
                "publicationEligible": publication_eligible,
                "provenanceRef": provenance_ref,
                "reason": reason,
                "conflict": conflict,
            }
        )

    expected = {(vehicle_id, field) for vehicle_id in {row["vehicleId"] for row in normalized} for field in CONTRACT_FIELDS}
    actual = {(row["vehicleId"], row["field"]) for row in normalized}
    if actual != expected:
        missing = sorted(expected - actual)
        raise ValueError(f"fixture must cover every contract field for every retained vehicle; missing={missing}")

    control = payload.get("structuralControl")
    if not isinstance(control, dict) or control.get("sourceFamily") == source.get("family"):
        raise ValueError("structural control must be present and separate from Brazil source family")
    _text(control.get("sourceFamily"), "structuralControl.sourceFamily")
    _text(control.get("provenanceRef"), "structuralControl.provenanceRef")

    return {
        "schema": COVERAGE_SCHEMA,
        "corpusVersion": payload["corpusVersion"],
        "source": source,
        "records": sorted(normalized, key=lambda row: (row["field"], row["vehicleId"])),
        "structuralControl": control,
    }


def records_comparable(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["vehicleId"] == right["vehicleId"]:
        return False
    if not left["publicationEligible"] or not right["publicationEligible"]:
        return False
    if left["knowledgeState"] != "known" or right["knowledgeState"] != "known":
        return False
    if left["field"] != right["field"] or left["unit"] != right["unit"]:
        return False
    return left.get("context", {}) == right.get("context", {})


def run_coverage_benchmark(path: str | Path) -> dict[str, Any]:
    fixture = load_coverage_fixture(path)
    records = fixture["records"]
    by_field: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_field[record["field"]].append(record)

    fields: list[dict[str, Any]] = []
    for field in sorted(CONTRACT_FIELDS):
        rows = by_field[field]
        comparable_vehicle_ids: set[str] = set()
        for index, left in enumerate(rows):
            for right in rows[index + 1 :]:
                if records_comparable(left, right):
                    comparable_vehicle_ids.add(left["vehicleId"])
                    comparable_vehicle_ids.add(right["vehicleId"])
        shapes = Counter(row["valueShape"] for row in rows if row["valueShape"] is not None)
        provenance = Counter(row["provenanceRef"] for row in rows)
        fields.append(
            {
                "field": field,
                "denominator": len(rows),
                "knownPublicationReady": sum(row["knowledgeState"] == "known" and row["publicationEligible"] for row in rows),
                "unknownOrNotPublishable": sum(not row["publicationEligible"] for row in rows),
                "unresolvedConflict": sum(row["conflict"] is not None for row in rows),
                "shapeDistribution": dict(sorted(shapes.items())),
                "provenanceDistribution": dict(sorted(provenance.items())),
                "vehiclesComparableWithDistinctPeer": len(comparable_vehicle_ids),
            }
        )

    material = {
        "schema": RESULT_SCHEMA,
        "corpusVersion": fixture["corpusVersion"],
        "source": fixture["source"],
        "records": records,
        "fields": fields,
        "structuralControl": fixture["structuralControl"],
    }
    material["contentSha256"] = hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()
    return material


def summarize_coverage_result(result: dict[str, Any]) -> dict[str, Any]:
    records = result["records"]
    total_records = len(records)
    known = sum(row["knowledgeState"] == "known" for row in records)
    unknown = sum(row["knowledgeState"] == "unknown" for row in records)
    not_applicable = sum(row["knowledgeState"] == "not_applicable" for row in records)
    publication_ready = sum(row["knowledgeState"] == "known" and row["publicationEligible"] for row in records)
    normalized = sum(row["knowledgeState"] == "known" and row["value"] is not None and row["unit"] is not None for row in records)
    provenance_complete = sum(bool(row["provenanceRef"]) for row in records)
    blocked = total_records - publication_ready
    blocked_by_reason = Counter(row["reason"] or "publication_ready" for row in records if not row["publicationEligible"])

    by_vehicle: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_source: Counter[str] = Counter()
    for record in records:
        by_vehicle[record["vehicleId"]].append(record)
        by_source[record["provenanceRef"]] += 1

    vehicle_coverage = []
    fully_publication_ready = 0
    partially_publication_ready = 0
    for vehicle_id, rows in sorted(by_vehicle.items()):
        vehicle_ready = sum(row["knowledgeState"] == "known" and row["publicationEligible"] for row in rows)
        if vehicle_ready == len(rows):
            fully_publication_ready += 1
        elif vehicle_ready:
            partially_publication_ready += 1
        vehicle_coverage.append(
            {
                "vehicleId": vehicle_id,
                "totalFields": len(rows),
                "publicationReadyFields": vehicle_ready,
                "blockedFields": len(rows) - vehicle_ready,
            }
        )

    return {
        "schema": "podium7.quantitative-coverage-summary.v1",
        "corpusVersion": result["corpusVersion"],
        "source": result["source"],
        "contentSha256": result["contentSha256"],
        "totalVehicles": len(by_vehicle),
        "totalCandidateQuantitativeFacts": total_records,
        "known": known,
        "unknown": unknown,
        "notApplicable": not_applicable,
        "normalized": normalized,
        "provenanceComplete": provenance_complete,
        "publicationReady": publication_ready,
        "blocked": blocked,
        "blockedByReason": dict(sorted(blocked_by_reason.items())),
        "perFieldCoverage": result["fields"],
        "perSourceCoverage": dict(sorted(by_source.items())),
        "perVehicleCoverage": vehicle_coverage,
        "fullyPublicationReadyVehicles": fully_publication_ready,
        "partiallyPublicationReadyVehicles": partially_publication_ready,
    }


def render_coverage_result(path: str | Path) -> str:
    return json.dumps(run_coverage_benchmark(path), ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"


__all__ = [
    "COVERAGE_SCHEMA",
    "RESULT_SCHEMA",
    "load_coverage_fixture",
    "records_comparable",
    "render_coverage_result",
    "run_coverage_benchmark",
    "summarize_coverage_result",
]
