from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_operational import build_source_backed_operational_records
from .evidence_enrichment import build_source_backed_enrichment_work
from .enrichment_quality import measure_enriched_operational_corpus
from .source_backed_enrichment import (
    apply_source_backed_overrides_to_records,
    load_source_backed_enrichment_overrides,
)


REVIEW_DISPOSITION_SCHEMA = "podium7.review-disposition.v1"
DURABLE_HUMAN_REVIEW = "HUMAN_REVIEW_EVIDENCE_EXHAUSTED"


def _provenance_cases(paths: Iterable[str | Path]) -> dict[str, set[str]]:
    cases: dict[str, set[str]] = {}
    for raw_path in paths:
        payload = json.loads(Path(raw_path).read_text(encoding="utf-8"))
        if payload.get("schema") != "podium7.catalog-identity-golden.v1":
            raise ValueError("unsupported source-backed benchmark schema")
        for case in payload.get("cases", ()):
            case_id = case.get("id")
            source_ids = case.get("sourceIds")
            if not isinstance(case_id, str) or not case_id.strip():
                raise ValueError("benchmark case id is required")
            if not isinstance(source_ids, list) or not source_ids:
                raise ValueError(f"benchmark case {case_id!r} requires sourceIds")
            if case_id in cases:
                raise ValueError(f"duplicate benchmark case id {case_id!r}")
            cases[case_id] = {str(value) for value in source_ids}
    return cases


def load_review_dispositions(
    paths: Iterable[str | Path],
    disposition_path: str | Path,
) -> dict[str, dict[str, Any]]:
    benchmark_cases = _provenance_cases(paths)
    payload = json.loads(Path(disposition_path).read_text(encoding="utf-8"))
    if payload.get("schema") != REVIEW_DISPOSITION_SCHEMA:
        raise ValueError("unsupported review disposition schema")
    decisions = payload.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("review disposition decisions are required")

    result: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise ValueError("review disposition decision must be an object")
        case_id = decision.get("caseId")
        disposition = decision.get("disposition")
        source_ids = decision.get("sourceIds")
        rationale = decision.get("rationale")
        evidence_status = decision.get("evidenceStatus")
        if not isinstance(case_id, str) or case_id not in benchmark_cases:
            raise ValueError(f"unknown review disposition case {case_id!r}")
        if case_id in result:
            raise ValueError(f"duplicate review disposition case {case_id!r}")
        if disposition != DURABLE_HUMAN_REVIEW:
            raise ValueError(f"unsupported review disposition {disposition!r}")
        if not isinstance(source_ids, list) or not source_ids:
            raise ValueError(f"review disposition {case_id!r} requires sourceIds")
        source_set = {str(value) for value in source_ids}
        if not source_set.issubset(benchmark_cases[case_id]):
            raise ValueError(
                f"review disposition {case_id!r} uses a source outside case provenance"
            )
        if evidence_status not in {"LIVE_REVALIDATED", "REPOSITORY_CURATED"}:
            raise ValueError(f"review disposition {case_id!r} has invalid evidenceStatus")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"review disposition {case_id!r} requires rationale")
        result[case_id] = dict(decision)
    return result


def evaluate_review_dispositions(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
    disposition_path: str | Path,
) -> dict[str, Any]:
    dataset_paths = tuple(paths)
    overrides = load_source_backed_enrichment_overrides(dataset_paths, enrichment_path)
    records = build_source_backed_operational_records(dataset_paths)
    records = apply_source_backed_overrides_to_records(records, overrides)
    store = CatalogStore()
    ingest_catalog_batch(store, parse_catalog_batch_payload({"records": records}))
    work = build_source_backed_enrichment_work(store, dataset_paths)
    diagnostics = measure_enriched_operational_corpus(dataset_paths, enrichment_path)
    reasons = diagnostics["reviewReasonsByEvidence"]
    candidates = diagnostics["reviewCandidatesByEvidence"]
    dispositions = load_review_dispositions(dataset_paths, disposition_path)

    current_case_ids = {item["caseId"] for item in work["items"]}
    unused_disposition_case_ids = sorted(set(dispositions) - current_case_ids)

    durable: list[dict[str, Any]] = []
    unassessed: list[dict[str, Any]] = []
    for item in work["items"]:
        decision = dispositions.get(item["caseId"])
        if decision is None:
            unassessed.append(
                {
                    **item,
                    "reviewReasons": reasons.get(item["evidenceId"], []),
                    "reviewCandidates": candidates.get(item["evidenceId"], []),
                }
            )
            continue
        durable.append(
            {
                **item,
                "originalDisposition": item["disposition"],
                "disposition": decision["disposition"],
                "evidenceStatus": decision["evidenceStatus"],
                "dispositionSourceIds": list(decision["sourceIds"]),
                "dispositionRationale": decision["rationale"],
            }
        )

    blocked = list(work["blockedItems"])
    return {
        "schema": "podium7.production-review-disposition-report.v1",
        "summary": {
            "openReviews": work["summary"]["openReviews"],
            "durableHumanReview": len(durable),
            "unassessed": len(unassessed),
            "unusedDispositions": len(unused_disposition_case_ids),
            "blocked": len(blocked),
            "resolverPolicyChanges": 0,
        },
        "unassessedCaseIds": sorted({item["caseId"] for item in unassessed}),
        "unusedDispositionCaseIds": unused_disposition_case_ids,
        "durableHumanReviewItems": durable,
        "unassessedItems": unassessed,
        "blockedItems": blocked,
    }


__all__ = [
    "DURABLE_HUMAN_REVIEW",
    "REVIEW_DISPOSITION_SCHEMA",
    "evaluate_review_dispositions",
    "load_review_dispositions",
]
