from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import ingest_catalog_record
from podium7.domain import RawEvidence, Source


def _required_object(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value.strip()


def _timestamp(value: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("evidence.retrievedAt must include a timezone")
    return parsed


def _load_envelope(path: Path) -> tuple[dict[str, Any], Source, RawEvidence]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("input must be a JSON object")

    source_payload = _required_object(payload, "source")
    evidence_payload = _required_object(payload, "evidence")
    vehicle = _required_object(payload, "vehicle")

    source = Source(
        id=_required_text(source_payload, "id"),
        name=_required_text(source_payload, "name"),
        locator=_required_text(source_payload, "locator"),
    )
    evidence = RawEvidence(
        id=_required_text(evidence_payload, "id"),
        source_id=source.id,
        locator=_required_text(evidence_payload, "locator"),
        retrieved_at=_timestamp(_required_text(evidence_payload, "retrievedAt")),
        acquisition_method=_required_text(evidence_payload, "acquisitionMethod"),
        raw_content_ref=_required_text(evidence_payload, "rawContentRef"),
    )
    return vehicle, source, evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest one evidence-backed vehicle record into the Podium 7 Catalog"
    )
    parser.add_argument("input", type=Path, help="JSON envelope with source, evidence and vehicle")
    parser.add_argument("--database", type=Path, default=Path("podium7.sqlite"))
    args = parser.parse_args(argv)

    try:
        vehicle, source, evidence = _load_envelope(args.input)
        with CatalogStore(args.database) as store:
            result = ingest_catalog_record(
                store,
                vehicle,
                source=source,
                evidence=evidence,
            )
        print(json.dumps({"ok": True, **result.to_payload()}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"ok": False, "error": {"code": "CATALOG_INGESTION_INVALID_INPUT", "message": str(exc)}},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
