from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


BASELINE_SCHEMA = "podium7.identity-safety-baseline.v1"
_RATE_METRICS = ("autoMatchPrecision", "autoMatchRecall")
_COUNT_METRICS = ("falseMergeCount", "ambiguousOvercommitCount")
_METRICS = _RATE_METRICS + _COUNT_METRICS


def _validate_metrics(metrics: Mapping[str, Any], *, label: str) -> None:
    for metric in _METRICS:
        if metric not in metrics:
            raise ValueError(f"{label} metric is required: {metric}")
        value = metrics[metric]
        if metric in _RATE_METRICS:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or not 0.0 <= value <= 1.0
            ):
                raise ValueError(f"{label} metric {metric} must be a finite number between 0 and 1")
        else:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{label} metric {metric} must be a non-negative integer")


def _validate_datasets(value: Any, *, label: str) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        raise ValueError(f"{label} datasets must be a non-empty sequence")
    datasets = list(value)
    if any(not isinstance(item, str) or not item.strip() for item in datasets):
        raise ValueError(f"{label} datasets must be non-empty text values")
    if len(set(datasets)) != len(datasets):
        raise ValueError(f"{label} datasets must be unique")
    return datasets


def _validate_total_cases(value: Any, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} totalCases must be a positive integer")
    return value


def _validate_baseline_payload(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != BASELINE_SCHEMA:
        raise ValueError("unsupported identity safety baseline schema")
    baseline_version = payload.get("baselineVersion")
    if not isinstance(baseline_version, str) or not baseline_version.strip():
        raise ValueError("baselineVersion is required")
    source_document = payload.get("sourceDocument")
    if not isinstance(source_document, str) or not source_document.strip():
        raise ValueError("sourceDocument is required")
    _validate_datasets(payload.get("datasets"), label="baseline")
    _validate_total_cases(payload.get("totalCases"), label="baseline")
    metrics = payload.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("baseline metrics are required")
    _validate_metrics(metrics, label="baseline")


def load_identity_safety_baseline(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("identity safety baseline must be an object")
    _validate_baseline_payload(payload)
    return dict(payload)


def compare_identity_quality_to_baseline(
    quality_report: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(quality_report, Mapping):
        raise ValueError("identity quality report must be an object")
    if not isinstance(baseline, Mapping):
        raise ValueError("identity safety baseline must be an object")
    _validate_baseline_payload(baseline)

    datasets = _validate_datasets(quality_report.get("datasets"), label="identity quality")
    expected_datasets = _validate_datasets(baseline.get("datasets"), label="baseline")
    if datasets != expected_datasets:
        raise ValueError("identity baseline dataset contract mismatch")

    total_cases = _validate_total_cases(quality_report.get("totalCases"), label="identity quality")
    expected_total_cases = _validate_total_cases(baseline.get("totalCases"), label="baseline")
    if total_cases != expected_total_cases:
        raise ValueError("identity baseline case-count contract mismatch")

    metrics = quality_report.get("metrics")
    baseline_metrics = baseline.get("metrics")
    if not isinstance(metrics, Mapping) or not isinstance(baseline_metrics, Mapping):
        raise ValueError("identity quality metrics are required")
    _validate_metrics(baseline_metrics, label="baseline")
    _validate_metrics(metrics, label="identity quality")

    comparisons: dict[str, dict[str, Any]] = {}
    regressions: list[str] = []
    for metric in _METRICS:
        current = metrics[metric]
        expected = baseline_metrics[metric]
        if metric in _RATE_METRICS:
            passed = current >= expected
            delta = current - expected
        else:
            passed = current <= expected
            delta = current - expected
        comparisons[metric] = {
            "baseline": expected,
            "current": current,
            "delta": delta,
            "passed": passed,
        }
        if not passed:
            regressions.append(metric)

    return {
        "schema": "podium7.identity-safety-regression.v1",
        "baselineVersion": baseline["baselineVersion"],
        "datasets": datasets,
        "totalCases": total_cases,
        "passed": not regressions,
        "regressions": regressions,
        "metrics": comparisons,
    }


__all__ = [
    "BASELINE_SCHEMA",
    "compare_identity_quality_to_baseline",
    "load_identity_safety_baseline",
]
