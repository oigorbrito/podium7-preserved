from __future__ import annotations

from typing import Any, Mapping

from .catalog_benchmark import CatalogBenchmarkDataset, evaluate_catalog_identity_benchmark
from .heterogeneity_benchmark import evaluate_heterogeneity_slices


def podium_safety_metrics_from_catalog_report(report: Mapping[str, Any]) -> dict[str, int | float | None]:
    metrics = report.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("catalog benchmark report metrics are required")
    required = (
        "matchPrecision",
        "matchRecall",
        "falseMergeCount",
        "missedDuplicateCount",
        "ambiguousOvercommitCount",
        "reviewRate",
    )
    missing = [key for key in required if key not in metrics]
    if missing:
        raise ValueError("catalog benchmark report is missing metrics: " + ", ".join(missing))
    return {
        "autoMatchPrecision": metrics["matchPrecision"],
        "autoMatchRecall": metrics["matchRecall"],
        "falseMergeCount": metrics["falseMergeCount"],
        "missedMatchCount": metrics["missedDuplicateCount"],
        "ambiguousOvercommitCount": metrics["ambiguousOvercommitCount"],
        "reviewRate": metrics["reviewRate"],
    }


def _gold_signature(dataset: CatalogBenchmarkDataset) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((case.id, case.expected.value) for case in dataset.cases))


def compare_catalog_heterogeneity(
    clean: CatalogBenchmarkDataset,
    slices: Mapping[str, CatalogBenchmarkDataset],
) -> dict[str, Any]:
    if not isinstance(clean, CatalogBenchmarkDataset):
        raise ValueError("clean must be CatalogBenchmarkDataset")
    if not isinstance(slices, Mapping) or not slices:
        raise ValueError("at least one catalog heterogeneity slice is required")
    clean_signature = _gold_signature(clean)
    clean_report = evaluate_catalog_identity_benchmark(clean)
    slice_metrics: dict[str, dict[str, int | float | None]] = {}
    for name, dataset in slices.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("slice names must be non-empty text")
        if not isinstance(dataset, CatalogBenchmarkDataset):
            raise ValueError("slice datasets must be CatalogBenchmarkDataset")
        if _gold_signature(dataset) != clean_signature:
            raise ValueError(
                f"heterogeneity slice {name!r} must preserve the clean case ids and expected labels"
            )
        slice_report = evaluate_catalog_identity_benchmark(dataset)
        slice_metrics[name] = podium_safety_metrics_from_catalog_report(slice_report)
    report = evaluate_heterogeneity_slices(
        podium_safety_metrics_from_catalog_report(clean_report),
        slice_metrics,
    )
    report["cleanDatasetVersion"] = clean.version
    report["sliceDatasetVersions"] = {
        name: dataset.version for name, dataset in sorted(slices.items())
    }
    return report


__all__ = ["compare_catalog_heterogeneity", "podium_safety_metrics_from_catalog_report"]
