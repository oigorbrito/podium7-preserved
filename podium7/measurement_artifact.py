from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


MEASUREMENT_ARTIFACT_SCHEMA = "podium7.production-quality-measurement-artifact.v1"
IDENTITY_QUALITY_SCHEMA = "podium7.production-identity-quality.v1"
OPERATIONAL_MEASUREMENT_SCHEMA = "podium7.production-operational-measurement.v1"
MEASUREMENT_CONTRACT_VERSION = "production-quality-measurement-v2"


def _dataset_descriptor(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"measurement dataset must be UTF-8 JSON: {path}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError(f"measurement dataset must be a JSON object: {path}")
    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"datasetVersion is required: {path}")
    return {
        "name": path.name,
        "datasetVersion": version,
        "sha256": sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _validate_measurement_report(
    report: Mapping[str, Any],
    *,
    expected_schema: str,
    label: str,
) -> dict[str, Any]:
    if not isinstance(report, Mapping):
        raise ValueError(f"{label} report must be an object")
    if report.get("schema") != expected_schema:
        raise ValueError(f"unsupported {label} report schema")
    try:
        json.dumps(report, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} report must be strict JSON-compatible") from exc
    return dict(report)


def build_measurement_artifact(
    paths: Iterable[str | Path],
    *,
    identity_quality: Mapping[str, Any],
    operational: Mapping[str, Any],
) -> dict[str, Any]:
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
    identity_report = _validate_measurement_report(
        identity_quality,
        expected_schema=IDENTITY_QUALITY_SCHEMA,
        label="identity quality",
    )
    operational_report = _validate_measurement_report(
        operational,
        expected_schema=OPERATIONAL_MEASUREMENT_SCHEMA,
        label="operational measurement",
    )

    identity_versions = identity_report.get("datasets")
    descriptor_versions = [item["datasetVersion"] for item in datasets]
    if identity_versions != descriptor_versions:
        raise ValueError("identity quality dataset versions do not match artifact inputs")

    return {
        "schema": MEASUREMENT_ARTIFACT_SCHEMA,
        "measurementContractVersion": MEASUREMENT_CONTRACT_VERSION,
        "datasets": datasets,
        "identityQuality": identity_report,
        "operational": operational_report,
    }


def measurement_artifact_json(
    paths: Iterable[str | Path],
    *,
    identity_quality: Mapping[str, Any],
    operational: Mapping[str, Any],
) -> str:
    return json.dumps(
        build_measurement_artifact(
            paths,
            identity_quality=identity_quality,
            operational=operational,
        ),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def write_measurement_artifact(
    path: str | Path,
    datasets: Iterable[str | Path],
    *,
    identity_quality: Mapping[str, Any],
    operational: Mapping[str, Any],
) -> Path:
    destination = Path(path)
    destination.write_text(
        measurement_artifact_json(
            datasets,
            identity_quality=identity_quality,
            operational=operational,
        ),
        encoding="utf-8",
    )
    return destination


__all__ = [
    "IDENTITY_QUALITY_SCHEMA",
    "MEASUREMENT_ARTIFACT_SCHEMA",
    "MEASUREMENT_CONTRACT_VERSION",
    "OPERATIONAL_MEASUREMENT_SCHEMA",
    "build_measurement_artifact",
    "measurement_artifact_json",
    "write_measurement_artifact",
]
