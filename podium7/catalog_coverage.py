from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_api import list_catalog_vehicles
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


def measure_published_catalog_identity_coverage(
    datasets: Iterable[Path],
) -> dict[str, Any]:
    dataset_paths = tuple(Path(path) for path in datasets)
    store = CatalogStore()
    operational = run_source_backed_operational_corpus(store, dataset_paths)
    consumer = list_catalog_vehicles(store, limit=100)
    if not consumer.get("ok"):
        raise RuntimeError(f"catalog consumer failed: {consumer}")

    items = consumer["items"]
    entities = [item["entity"] for item in items]
    return {
        "scope": "source-backed-production-corpus-v2-consumer-output",
        "datasets": [path.name for path in dataset_paths],
        "operational": {
            "total": operational.total,
            "created": operational.created,
            "matched": operational.matched,
            "review": operational.review,
            "failed": operational.failed,
            "ok": operational.ok,
        },
        "publishedVehicles": len(entities),
        "fields": {field: _field_report(entities, field) for field in MEASURED_FIELDS},
        "byMarket": _market_report(entities),
        "boundary": (
            "This is measured coverage on the bounded source-backed Production Corpus V2 "
            "after the real ingestion/resolution path and consumer export. It is not a claim "
            "of production-wide population coverage."
        ),
    }


__all__ = ["MEASURED_FIELDS", "measure_published_catalog_identity_coverage"]
