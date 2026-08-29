from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CATALOG_CONTRACT_DEFAULT_VERSION, CatalogStore
from .catalog_api import CATALOG_API_MAX_PAGE_SIZE, list_catalog_vehicles
from .operational_provenance import (
    measure_operational_provenance_eligibility,
    run_provenance_eligible_operational_corpus,
)


MEASURED_FIELDS = ("powertrain", "transmission", "body_style")
BRAZIL_MARKET = "BR"


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _field_report(entities: list[dict[str, Any]], field: str) -> dict[str, Any]:
    raw_values: list[str] = []
    unknown_null = 0
    normalized_to_raw: dict[str, set[str]] = defaultdict(set)
    for entity in entities:
        if field not in entity:
            raise ValueError(f"catalog contract field missing from consumer entity: {field}")
        value = entity[field]
        if value is None:
            unknown_null += 1
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"catalog contract field {field} must be non-empty string or null, got {value!r}"
            )
        raw = value.strip()
        raw_values.append(raw)
        normalized_to_raw[_normalized_text(raw)].add(raw)

    total = len(entities)
    present = len(raw_values)
    return {
        "present": present,
        "unknownNull": unknown_null,
        "coverage": present / total if total else 0.0,
        "rawDistinct": len(set(raw_values)),
        "normalizedDistinct": len(normalized_to_raw),
        "normalizationCollisions": {
            normalized: sorted(values)
            for normalized, values in sorted(normalized_to_raw.items())
            if len(values) > 1
        },
        "values": sorted(set(raw_values), key=lambda value: (value.casefold(), value)),
    }


def _market_key(entity: dict[str, Any]) -> str:
    if "market" not in entity:
        raise ValueError("catalog contract field missing from consumer entity: market")
    market = entity["market"]
    if market is None:
        return "<unknown:null>"
    if not isinstance(market, str) or not market.strip():
        raise ValueError(
            f"catalog contract field market must be non-empty string or null, got {market!r}"
        )
    return market.strip()


def _market_report(entities: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        grouped[_market_key(entity)].append(entity)

    return {
        market: {
            "total": len(items),
            "fields": {field: _field_report(items, field) for field in MEASURED_FIELDS},
        }
        for market, items in sorted(grouped.items())
    }


def _specific_market_report(
    entities: list[dict[str, Any]], market_code: str
) -> dict[str, Any]:
    items = [entity for entity in entities if _market_key(entity) == market_code]
    return {
        "market": market_code,
        "total": len(items),
        "fields": {field: _field_report(items, field) for field in MEASURED_FIELDS},
    }


def _consumer_entities(store: CatalogStore) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        consumer = list_catalog_vehicles(
            store,
            limit=CATALOG_API_MAX_PAGE_SIZE,
            cursor=cursor,
            contract_version=CATALOG_CONTRACT_DEFAULT_VERSION,
        )
        if not consumer.get("ok"):
            raise RuntimeError(f"catalog consumer failed: {consumer}")
        items = consumer["items"]
        entities.extend(item["entity"] for item in items)
        cursor = consumer.get("nextCursor")
        if cursor is None:
            return entities


def _operational_report(operational: Any) -> dict[str, Any]:
    return {
        "total": operational.total,
        "created": operational.created,
        "matched": operational.matched,
        "review": operational.review,
        "failed": operational.failed,
        "ok": operational.ok,
    }


def _empty_operational_report() -> dict[str, Any]:
    return {
        "total": 0,
        "created": 0,
        "matched": 0,
        "review": 0,
        "failed": 0,
        "ok": True,
    }


def _dataset_identity(path: Path) -> dict[str, str]:
    raw = path.read_bytes()
    payload = json.loads(raw)
    schema = payload.get("schema")
    dataset_version = payload.get("datasetVersion")
    if not isinstance(schema, str) or not schema:
        raise ValueError(f"dataset schema is required: {path}")
    if not isinstance(dataset_version, str) or not dataset_version:
        raise ValueError(f"datasetVersion is required: {path}")
    return {
        "name": path.name,
        "schema": schema,
        "datasetVersion": dataset_version,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _provenance_gated_replay(
    dataset_paths: tuple[Path, ...],
) -> tuple[CatalogStore, dict[str, Any], dict[str, Any]]:
    eligibility = measure_operational_provenance_eligibility(dataset_paths)
    store = CatalogStore()
    if eligibility["summary"]["replayableRecords"]:
        operational = _operational_report(
            run_provenance_eligible_operational_corpus(store, dataset_paths)
        )
    else:
        operational = _empty_operational_report()
    if operational["total"] != eligibility["summary"]["replayableRecords"]:
        raise RuntimeError("provenance eligibility and replay record counts diverged")
    return store, operational, eligibility["summary"]


def _dataset_report(path: Path) -> dict[str, Any]:
    store, operational, eligibility = _provenance_gated_replay((path,))
    entities = _consumer_entities(store)
    return {
        "dataset": _dataset_identity(path),
        "total": len(entities),
        "operational": operational,
        "provenanceEligibility": eligibility,
        "fields": {field: _field_report(entities, field) for field in MEASURED_FIELDS},
        "byMarket": _market_report(entities),
        "brazil": _specific_market_report(entities, BRAZIL_MARKET),
    }


def measure_published_catalog_identity_coverage(
    datasets: Iterable[Path],
) -> dict[str, Any]:
    dataset_paths = tuple(Path(path) for path in datasets)
    store, operational, eligibility = _provenance_gated_replay(dataset_paths)
    entities = _consumer_entities(store)
    return {
        "scope": "provenance-gated-source-backed-consumer-output",
        "contractVersion": CATALOG_CONTRACT_DEFAULT_VERSION,
        "datasets": [_dataset_identity(path) for path in dataset_paths],
        "operational": operational,
        "provenanceEligibility": eligibility,
        "publishedVehicles": len(entities),
        "fields": {field: _field_report(entities, field) for field in MEASURED_FIELDS},
        "byMarket": _market_report(entities),
        "brazil": _specific_market_report(entities, BRAZIL_MARKET),
        "byDataset": {
            path.name: _dataset_report(path)
            for path in dataset_paths
        },
        "reviewEvidence": {
            "count": operational["review"],
            "granularity": "aggregate-provenance-eligible-operational",
            "fieldAttributionAvailable": False,
            "note": (
                "Review count covers only provenance-eligible operational records. Blocked "
                "record sides are reported separately under provenanceEligibility and are not "
                "silently attributed or replayed."
            ),
        },
        "knowledgeState": {
            "known": "non-empty string",
            "unknown": "JSON null",
            "note": (
                "Catalog contract 2.0 guarantees these measured keys are present and uses null "
                "when their value is unknown. Missing keys, blank strings and other JSON types "
                "are treated as contract violations rather than coverage misses."
            ),
        },
        "boundary": (
            "This is measured field coverage only on the provenance-eligible subset of the "
            "bounded retained source-backed corpus after real ingestion/resolution and fully "
            "paginated consumer export. provenanceEligibility reports the complete retained "
            "record-side universe and the blocked portion. Blocked records are excluded rather "
            "than assigned a source by list position. Dataset versions and SHA-256 digests bind "
            "the report to exact inputs. This is neither production-wide population coverage "
            "nor evidence that blocked sides have missing field values."
        ),
    }


__all__ = [
    "BRAZIL_MARKET",
    "MEASURED_FIELDS",
    "measure_published_catalog_identity_coverage",
]
