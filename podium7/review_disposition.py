from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from .evidence_enrichment import build_source_backed_enrichment_work
from .enrichment_quality import measure_enriched_operational_corpus
from .operational_provenance import (
    build_provenance_eligible_operational_records,
    measure_operational_provenance_eligibility,
)
from .source_backed_enrichment import (
    apply_source_backed_overrides_to_records,
    load_source_backed_enrichment_overrides,
)


REVIEW_DISPOSITION_SCHEMA = "podium7.review-disposition.v3"
DURABLE_HUMAN_REVIEW = "HUMAN_REVIEW_EVIDENCE_EXHAUSTED"
_VALID_SIDES = {"left", "right"}


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
            if (
                not isinstance(source_ids, list)
                or not source_ids
                or any(not isinstance(value, str) or not value.strip() for value in source_ids)
                or len(set(source_ids)) != len(source_ids)
            ):
                raise ValueError(
                    f"benchmark case {case_id!r} requires unique non-empty sourceIds"
                )
            if case_id in cases:
                raise ValueError(f"duplicate benchmark case id {case_id!r}")
            cases[case_id] = set(source_ids)
    return cases


def load_review_dispositions(
    paths: Iterable[str | Path],
    disposition_path: str | Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    benchmark_cases = _provenance_cases(paths)
    payload = json.loads(Path(disposition_path).read_text(encoding="utf-8"))
    if payload.get("schema") != REVIEW_DISPOSITION_SCHEMA:
        raise ValueError("unsupported review disposition schema")
    decisions = payload.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("review disposition decisions are required")

    result: dict[tuple[str, str], dict[str, Any]] = {}
    seen_cases: set[str] = set()
    for decision in decisions:
        if not isinstance(decision, dict):
            raise ValueError("review disposition decision must be an object")
        case_id = decision.get("caseId")
        sides = decision.get("sides")
        evidence_ids_by_side = decision.get("evidenceIdsBySide")
        disposition = decision.get("disposition")
        source_ids = decision.get("sourceIds")
        rationale = decision.get("rationale")
        evidence_status = decision.get("evidenceStatus")
        if not isinstance(case_id, str) or case_id not in benchmark_cases:
            raise ValueError(f"unknown review disposition case {case_id!r}")
        if case_id in seen_cases:
            raise ValueError(f"duplicate review disposition case {case_id!r}")
        seen_cases.add(case_id)
        if (
            not isinstance(sides, list)
            or not sides
            or any(not isinstance(side, str) or side not in _VALID_SIDES for side in sides)
            or len(set(sides)) != len(sides)
        ):
            raise ValueError(
                f"review disposition {case_id!r} requires unique left/right sides"
            )
        if (
            not isinstance(evidence_ids_by_side, dict)
            or set(evidence_ids_by_side) != set(sides)
            or any(
                not isinstance(value, str) or not value.strip()
                for value in evidence_ids_by_side.values()
            )
            or len(set(evidence_ids_by_side.values())) != len(evidence_ids_by_side)
        ):
            raise ValueError(
                f"review disposition {case_id!r} requires one unique evidenceId per side"
            )
        if disposition != DURABLE_HUMAN_REVIEW:
            raise ValueError(f"unsupported review disposition {disposition!r}")
        if (
            not isinstance(source_ids, list)
            or not source_ids
            or any(not isinstance(value, str) or not value.strip() for value in source_ids)
            or len(set(source_ids)) != len(source_ids)
        ):
            raise ValueError(
                f"review disposition {case_id!r} requires unique non-empty sourceIds"
            )
        source_set = set(source_ids)
        if not source_set.issubset(benchmark_cases[case_id]):
            raise ValueError(
                f"review disposition {case_id!r} uses a source outside case provenance"
            )
        if evidence_status not in {"LIVE_REVALIDATED", "REPOSITORY_CURATED"}:
            raise ValueError(f"review disposition {case_id!r} has invalid evidenceStatus")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(f"review disposition {case_id!r} requires rationale")
        for side in sides:
            result[(case_id, side)] = {
                **decision,
                "side": side,
                "evidenceId": evidence_ids_by_side[side],
            }
    return result


def _review_item_key_payload(
    keys: Iterable[tuple[str, str, str]],
) -> list[dict[str, str]]:
    return [
        {"caseId": case_id, "side": side, "evidenceId": evidence_id}
        for case_id, side, evidence_id in sorted(keys)
    ]


def evaluate_review_dispositions(
    paths: Iterable[str | Path],
    enrichment_path: str | Path,
    disposition_path: str | Path,
) -> dict[str, Any]:
    dataset_paths = tuple(paths)
    overrides = load_source_backed_enrichment_overrides(dataset_paths, enrichment_path)
    eligibility = measure_operational_provenance_eligibility(dataset_paths)
    records = build_provenance_eligible_operational_records(dataset_paths)
    replayable_evidence_ids = {record["evidence"]["id"] for record in records}
    operational_overrides = {
        evidence_id: field_values
        for evidence_id, field_values in overrides.items()
        if evidence_id in replayable_evidence_ids
    }
    records = apply_source_backed_overrides_to_records(records, operational_overrides)
    store = CatalogStore()
    ingest_catalog_batch(store, parse_catalog_batch_payload({"records": records}))
    work = build_source_backed_enrichment_work(store, dataset_paths)
    diagnostics = measure_enriched_operational_corpus(dataset_paths, enrichment_path)
    reasons = diagnostics["reviewReasonsByEvidence"]
    candidates = diagnostics["reviewCandidatesByEvidence"]
    dispositions = load_review_dispositions(dataset_paths, disposition_path)

    current_review_item_keys = {
        (item["caseId"], item["side"], item["evidenceId"])
        for item in work["items"]
    }
    disposition_by_item_key = {
        (case_id, side, decision["evidenceId"]): decision
        for (case_id, side), decision in dispositions.items()
    }
    provenance_blocked_item_keys = {
        (
            record["caseId"],
            record["side"],
            f"operational:{record['datasetVersion']}:{record['caseId']}:{record['side']}",
        )
        for record in eligibility["records"]
        if not record["replayable"]
    }
    provenance_blocked_disposition_item_keys = (
        set(disposition_by_item_key) & provenance_blocked_item_keys
    )
    unused_disposition_item_keys = (
        set(disposition_by_item_key)
        - current_review_item_keys
        - provenance_blocked_disposition_item_keys
    )

    durable: list[dict[str, Any]] = []
    unassessed: list[dict[str, Any]] = []
    for item in work["items"]:
        item_key = (item["caseId"], item["side"], item["evidenceId"])
        decision = disposition_by_item_key.get(item_key)
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
    unassessed_item_keys = {
        (item["caseId"], item["side"], item["evidenceId"])
        for item in unassessed
    }
    return {
        "schema": "podium7.production-review-disposition-report.v3",
        "summary": {
            "openReviews": work["summary"]["openReviews"],
            "durableHumanReview": len(durable),
            "unassessed": len(unassessed),
            "unusedDispositions": len(unused_disposition_item_keys),
            "provenanceBlockedDispositions": len(provenance_blocked_disposition_item_keys),
            "blocked": len(blocked),
            "resolverPolicyChanges": 0,
        },
        "provenanceEligibility": eligibility["summary"],
        "unassessedCaseIds": sorted({item["caseId"] for item in unassessed}),
        "unusedDispositionCaseIds": sorted(
            {case_id for case_id, _, _ in unused_disposition_item_keys}
        ),
        "provenanceBlockedDispositionCaseIds": sorted(
            {case_id for case_id, _, _ in provenance_blocked_disposition_item_keys}
        ),
        "unassessedReviewKeys": _review_item_key_payload(unassessed_item_keys),
        "unusedDispositionKeys": _review_item_key_payload(
            unused_disposition_item_keys
        ),
        "provenanceBlockedDispositionKeys": _review_item_key_payload(
            provenance_blocked_disposition_item_keys
        ),
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
