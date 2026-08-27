from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


REPORT_SCHEMA = "podium7.heterogeneity-stress-benchmark.v1"
_REQUIRED_RATE_KEYS = ("autoMatchPrecision", "autoMatchRecall", "reviewRate")
_REQUIRED_COUNT_KEYS = ("falseMergeCount", "missedMatchCount", "ambiguousOvercommitCount")


@dataclass(frozen=True)
class HeterogeneitySlice:
    name: str
    metrics: Mapping[str, int | float | None]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("slice name must be non-empty text")
        _validated_metrics(self.metrics)


def _validated_metrics(metrics: Mapping[str, int | float | None]) -> dict[str, int | float | None]:
    if not isinstance(metrics, Mapping):
        raise ValueError("metrics must be a mapping")
    missing = [key for key in _REQUIRED_RATE_KEYS + _REQUIRED_COUNT_KEYS if key not in metrics]
    if missing:
        raise ValueError("missing required metrics: " + ", ".join(missing))

    normalized: dict[str, int | float | None] = dict(metrics)
    for key in _REQUIRED_RATE_KEYS:
        value = normalized[key]
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be numeric or null")
        numeric = float(value)
        if numeric < 0 or numeric > 1:
            raise ValueError(f"{key} must be between 0 and 1")
        normalized[key] = numeric

    for key in _REQUIRED_COUNT_KEYS:
        value = normalized[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{key} must be a non-negative integer")
    return normalized


def _delta(current: int | float | None, baseline: int | float | None) -> float | None:
    if current is None or baseline is None:
        return None
    return float(current) - float(baseline)


def evaluate_heterogeneity_slices(
    clean_metrics: Mapping[str, int | float | None],
    slices: Mapping[str, Mapping[str, int | float | None]],
) -> dict[str, Any]:
    baseline = _validated_metrics(clean_metrics)
    if not isinstance(slices, Mapping) or not slices:
        raise ValueError("at least one heterogeneity slice is required")
    if any(not isinstance(name, str) or not name.strip() for name in slices):
        raise ValueError("slice names must be non-empty text")

    results: list[dict[str, Any]] = []
    for name, raw_metrics in sorted(slices.items()):
        current = _validated_metrics(raw_metrics)
        result = {
            "slice": name,
            "metrics": current,
            "deltas": {
                "precisionDelta": _delta(current["autoMatchPrecision"], baseline["autoMatchPrecision"]),
                "recallDelta": _delta(current["autoMatchRecall"], baseline["autoMatchRecall"]),
                "falseMergeDelta": _delta(current["falseMergeCount"], baseline["falseMergeCount"]),
                "missedMatchDelta": _delta(current["missedMatchCount"], baseline["missedMatchCount"]),
                "ambiguousOvercommitDelta": _delta(
                    current["ambiguousOvercommitCount"], baseline["ambiguousOvercommitCount"]
                ),
                "reviewRateDelta": _delta(current["reviewRate"], baseline["reviewRate"]),
            },
        }
        result["safetyRegression"] = bool(
            result["deltas"]["falseMergeDelta"] > 0
            or result["deltas"]["ambiguousOvercommitDelta"] > 0
        )
        results.append(result)

    return {
        "schema": REPORT_SCHEMA,
        "cleanBaseline": baseline,
        "slices": results,
        "safetyRegressionSliceCount": sum(bool(item["safetyRegression"]) for item in results),
    }


__all__ = ["HeterogeneitySlice", "REPORT_SCHEMA", "evaluate_heterogeneity_slices"]
