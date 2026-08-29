from __future__ import annotations

from collections import Counter
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
    false_merge = sum(case["expected"] == "NO_MATCH" and case["predicted"] == "MATCH" for case in cases)
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


def classify_review_reason(reason: str) -> str:
    if reason in {"model_year evidence is incomplete", "trim-defining evidence is incomplete", "insufficient deterministic identity evidence"}:
        return "MISSING_IDENTITY_EVIDENCE"
    if reason in {
        "STRONG external identifiers do not establish a shared identity",
        "SUPPORTING external identifiers do not establish a shared identity",
    }:
        return "IDENTIFIER_CONFLICT"
    if reason == "model labels partially overlap":
        return "LABEL_AMBIGUITY"
    return "UNKNOWN_REVIEW_CAUSE"


def review_disposition(cause: str) -> str:
    if cause == "MISSING_IDENTITY_EVIDENCE":
        return "ENRICH_THEN_REVIEW"
    if cause == "LABEL_AMBIGUITY":
        return "ENRICH_THEN_REVIEW"
    if cause == "IDENTIFIER_CONFLICT":
        return "HUMAN_REVIEW_REQUIRED"
    if cause == "UNKNOWN_REVIEW_CAUSE":
        return "BLOCK_AND_INVESTIGATE"
    raise ValueError(f"unknown review cause {cause!r}")


def analyze_review_cases(quality_report: dict[str, Any]) -> dict[str, Any]:
    review_cases = [case for case in quality_report.get("cases", ()) if case.get("predicted") == "REVIEW"]
    classified = [
        {
            **case,
            "cause": classify_review_reason(str(case.get("reason", ""))),
        }
        for case in review_cases
    ]
    classified = [
        {**case, "disposition": review_disposition(case["cause"])}
        for case in classified
    ]
    counts = Counter(case["cause"] for case in classified)
    unsafe = [case for case in classified if case.get("expected") != "REVIEW"]
    return {
        "schema": "podium7.review-analysis.v1",
        "totalReviews": len(classified),
        "causeCounts": dict(sorted(counts.items())),
        "unknownCauseCount": counts["UNKNOWN_REVIEW_CAUSE"],
        "unexpectedReviewCount": len(unsafe),
        "resolverChangeRequired": bool(unsafe or counts["UNKNOWN_REVIEW_CAUSE"]),
        "cases": classified,
    }


__all__ = [
    "analyze_review_cases",
    "classify_review_reason",
    "evaluate_identity_quality",
    "review_disposition",
]
