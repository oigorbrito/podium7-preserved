from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import CatalogBatchReport, ingest_catalog_batch, parse_catalog_batch_payload


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


__all__ = ["build_source_backed_operational_records", "run_source_backed_operational_corpus"]
