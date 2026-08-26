from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


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
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{label} metric {metric} must be a number between 0 and 1")
        else:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{label} metric {metric} must be a non-negative integer")


def load_identity_safety_baseline(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != BASELINE_SCHEMA:
        raise ValueError("unsupported identity safety baseline schema")
    datasets = payload.get("datasets")
    if not isinstance(datasets, list) or not datasets or any(not isinstance(item, str) or not item for item in datasets):
        raise ValueError("baseline datasets must be non-empty text values")
    if len(set(datasets)) != len(datasets):
        raise ValueError("baseline datasets must be unique")
    total_cases = payload.get("totalCases")
    if isinstance(total_cases, bool) or not isinstance(total_cases, int) or total_cases <= 0:
        raise ValueError("baseline totalCases must be a positive integer")
    metrics = payload.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("baseline metrics are required")
    _validate_metrics(metrics, label="baseline")
    return payload


def compare_identity_quality_to_baseline(
    quality_report: Mapping[str, Any],
    baseline: Mapping[str, Any],
) -> dict[str, Any]:
    datasets = list(quality_report.get("datasets", ()))
    expected_datasets = list(baseline.get("datasets", ()))
    if datasets != expected_datasets:
        raise ValueError("identity baseline dataset contract mismatch")
    total_cases = quality_report.get("totalCases")
    if total_cases != baseline.get("totalCases"):
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
        "baselineVersion": baseline.get("baselineVersion"),
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
