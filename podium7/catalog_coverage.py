from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .catalog import CATALOG_CONTRACT_DEFAULT_VERSION, CatalogStore
from .catalog_api import CATALOG_API_MAX_PAGE_SIZE, list_catalog_vehicles
from .catalog_operational import run_source_backed_operational_corpus


MEASURED_FIELDS = ("powertrain", "transmission", "body_style")


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _field_report(entities: list[dict[str, Any]], field: str) -> dict[str, Any]:
    raw_values: list[str] = []
    normalized_to_raw: dict[str, set[str]] = defaultdict(set)
    for entity in entities:
        value = entity.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        raw = value.strip()
        raw_values.append(raw)
        normalized_to_raw[_normalized_text(raw)].add(raw)

    total = len(entities)
    present = len(raw_values)
    return {
        "present": present,
        "missing": total - present,
        "coverage": present / total if total else 0.0,
        "rawDistinct": len(set(raw_values)),
        "normalizedDistinct": len(normalized_to_raw),
        "normalizationCollisions": {
            normalized: sorted(values)
            for normalized, values in sorted(normalized_to_raw.items())
            if len(values) > 1
        },
        "values": sorted(set(raw_values), key=str.casefold),
    }


def _market_report(entities: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities:
        market = entity.get("market")
        key = market.strip() if isinstance(market, str) and market.strip() else "<unknown>"
        grouped[key].append(entity)

    return {
        market: {
            "total": len(items),
            "fields": {field: _field_report(items, field) for field in MEASURED_FIELDS},
        }
        for market, items in sorted(grouped.items())
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


def _dataset_report(path: Path) -> dict[str, Any]:
    store = CatalogStore()
    operational = run_source_backed_operational_corpus(store, (path,))
    entities = _consumer_entities(store)
    return {
        "total": len(entities),
        "operational": _operational_report(operational),
        "fields": {field: _field_report(entities, field) for field in MEASURED_FIELDS},
        "byMarket": _market_report(entities),
    }


def measure_published_catalog_identity_coverage(
    datasets: Iterable[Path],
) -> dict[str, Any]:
    dataset_paths = tuple(Path(path) for path in datasets)
    store = CatalogStore()
    operational = run_source_backed_operational_corpus(store, dataset_paths)
    entities = _consumer_entities(store)
    return {
        "scope": "source-backed-production-corpus-v2-consumer-output",
        "contractVersion": CATALOG_CONTRACT_DEFAULT_VERSION,
        "datasets": [path.name for path in dataset_paths],
        "operational": _operational_report(operational),
        "publishedVehicles": len(entities),
        "fields": {field: _field_report(entities, field) for field in MEASURED_FIELDS},
        "byMarket": _market_report(entities),
        "byDataset": {
            path.name: _dataset_report(path)
            for path in dataset_paths
        },
        "reviewEvidence": {
            "count": operational.review,
            "granularity": "aggregate-operational",
            "fieldAttributionAvailable": False,
            "note": (
                "The existing operational corpus report exposes review count at aggregate run "
                "granularity only. This measurement does not invent field-level contradiction "
                "attribution when the pipeline does not publish it."
            ),
        },
        "boundary": (
            "This is measured coverage on the bounded source-backed Production Corpus V2 "
            "after the real ingestion/resolution path and fully paginated consumer export. "
            "Dataset breakdowns are measured through isolated replays of the same operational "
            "path and are evidence slices, not identity fields. It is not a claim of "
            "production-wide population coverage."
        ),
    }


__all__ = ["MEASURED_FIELDS", "measure_published_catalog_identity_coverage"]
