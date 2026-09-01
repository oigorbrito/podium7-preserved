from __future__ import annotations

import json
from pathlib import Path
import tempfile
from typing import Iterable

from .operational_multisource import (
    MULTISOURCE_FIELD_ATTRIBUTION_SCHEMA,
    build_multisource_operational_records,
    measure_combined_operational_provenance_eligibility,
)


def _compose_overlay_payload(attribution_paths: Iterable[str | Path]) -> dict:
    paths = tuple(Path(path) for path in attribution_paths)
    if not paths:
        raise ValueError("at least one multisource attribution overlay is required")

    mappings: list[dict] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != MULTISOURCE_FIELD_ATTRIBUTION_SCHEMA:
            raise ValueError("unsupported multisource field-attribution schema")
        raw_mappings = payload.get("mappings")
        if not isinstance(raw_mappings, list) or not raw_mappings:
            raise ValueError("multisource field attribution requires at least one mapping")
        mappings.extend(raw_mappings)

    return {
        "schema": MULTISOURCE_FIELD_ATTRIBUTION_SCHEMA,
        "datasetVersion": "composed-overlay-set-v1",
        "mappings": mappings,
    }


def _materialize_composed_overlay(attribution_paths: Iterable[str | Path], directory: str) -> Path:
    path = Path(directory) / "composed-operational-multisource-overlay.json"
    path.write_text(
        json.dumps(_compose_overlay_payload(attribution_paths), ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def build_multisource_operational_records_from_overlays(
    benchmark_paths: Iterable[str | Path],
    attribution_paths: Iterable[str | Path],
) -> list[dict]:
    with tempfile.TemporaryDirectory() as directory:
        path = _materialize_composed_overlay(attribution_paths, directory)
        return build_multisource_operational_records(benchmark_paths, path)


def measure_combined_operational_provenance_eligibility_from_overlays(
    benchmark_paths: Iterable[str | Path],
    attribution_paths: Iterable[str | Path],
) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        path = _materialize_composed_overlay(attribution_paths, directory)
        return measure_combined_operational_provenance_eligibility(benchmark_paths, path)


__all__ = [
    "build_multisource_operational_records_from_overlays",
    "measure_combined_operational_provenance_eligibility_from_overlays",
]
