from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog_operational import measure_source_backed_operational_corpus
from .catalog_quality import evaluate_identity_quality


MEASUREMENT_ARTIFACT_SCHEMA = "podium7.production-quality-measurement-artifact.v1"


def _dataset_descriptor(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"datasetVersion is required: {path}")
    return {
        "name": path.name,
        "datasetVersion": version,
        "sha256": sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def build_measurement_artifact(paths: Iterable[str | Path]) -> dict[str, Any]:
    normalized = tuple(Path(path) for path in paths)
    if not normalized:
        raise ValueError("measurement artifact requires at least one dataset")

    resolved = tuple(path.resolve() for path in normalized)
    if len(set(resolved)) != len(resolved):
        raise ValueError("measurement artifact dataset inputs must be unique")

    names = tuple(path.name for path in normalized)
    if len(set(names)) != len(names):
        raise ValueError("measurement artifact dataset names must be unique")

    datasets = [_dataset_descriptor(path) for path in normalized]
    return {
        "schema": MEASUREMENT_ARTIFACT_SCHEMA,
        "datasets": datasets,
        "identityQuality": evaluate_identity_quality(normalized),
        "operational": measure_source_backed_operational_corpus(normalized),
    }


def measurement_artifact_json(paths: Iterable[str | Path]) -> str:
    return json.dumps(
        build_measurement_artifact(paths),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def write_measurement_artifact(path: str | Path, datasets: Iterable[str | Path]) -> Path:
    destination = Path(path)
    destination.write_text(measurement_artifact_json(datasets), encoding="utf-8")
    return destination


__all__ = [
    "MEASUREMENT_ARTIFACT_SCHEMA",
    "build_measurement_artifact",
    "measurement_artifact_json",
    "write_measurement_artifact",
]
