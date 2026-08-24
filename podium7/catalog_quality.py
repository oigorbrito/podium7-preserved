from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .catalog_benchmark import evaluate_catalog_identity_benchmark, load_catalog_identity_benchmark


def evaluate_identity_quality(paths: Iterable[str | Path]) -> dict[str, Any]:
    reports = [evaluate_catalog_identity_benchmark(load_catalog_identity_benchmark(path)) for path in paths]
    if not reports:
        raise ValueError("at least one identity benchmark is required")

    cases = [case for report in reports for case in report["cases"]]
    expected_match = sum(case["expected"] == "MATCH" for case in cases)
    predicted_match = sum(case["predicted"] == "MATCH" for case in cases)
    true_match = sum(case["expected"] == "MATCH" and case["predicted"] == "MATCH" for case in cases)
    false_merge = sum(case["expected"] != "MATCH" and case["predicted"] == "MATCH" for case in cases)
    missed_match = sum(case["expected"] == "MATCH" and case["predicted"] != "MATCH" for case in cases)
    overcommit = sum(case["expected"] == "REVIEW" and case["predicted"] != "REVIEW" for case in cases)
    review = sum(case["predicted"] == "REVIEW" for case in cases)

    def rate(numerator: int, denominator: int) -> float | None:
        return numerator / denominator if denominator else None

    return {
        "schema": "podium7.production-identity-quality.v1",
        "datasets": [report["datasetVersion"] for report in reports],
        "totalCases": len(cases),
        "metrics": {
            "autoMatchPrecision": rate(true_match, predicted_match),
            "autoMatchRecall": rate(true_match, expected_match),
            "falseMergeCount": false_merge,
            "missedMatchCount": missed_match,
            "ambiguousOvercommitCount": overcommit,
            "reviewRate": rate(review, len(cases)),
        },
        "cases": cases,
    }


__all__ = ["evaluate_identity_quality"]
