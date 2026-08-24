from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_quality import classify_review_reason
from .catalog_review import CatalogReviewQueue


@dataclass(frozen=True)
class EvidenceEnrichmentWorkItem:
    review_id: str
    evidence_id: str
    case_id: str
    side: str
    cause: str
    disposition: str
    required_evidence: tuple[str, ...]
    source_ids: tuple[str, ...]
    source_locators: tuple[str, ...]
    candidate_vehicle_ids: tuple[str, ...]
    resolver_policy_change: bool = False

    def to_payload(self) -> dict[str, Any]:
        return {
            "reviewId": self.review_id,
            "evidenceId": self.evidence_id,
            "caseId": self.case_id,
            "side": self.side,
            "cause": self.cause,
            "disposition": self.disposition,
            "requiredEvidence": list(self.required_evidence),
            "sourceIds": list(self.source_ids),
            "sourceLocators": list(self.source_locators),
            "candidateVehicleIds": list(self.candidate_vehicle_ids),
            "resolverPolicyChange": self.resolver_policy_change,
        }


_REQUIREMENTS: dict[str, tuple[str, tuple[str, ...]]] = {
    "MISSING_IDENTITY_EVIDENCE": (
        "ENRICH_IDENTITY_EVIDENCE",
        ("source_backed_deterministic_identity_field",),
    ),
    "LABEL_AMBIGUITY": (
        "ENRICH_LABEL_EVIDENCE",
        ("source_backed_canonical_model_or_alias",),
    ),
    "IDENTIFIER_CONFLICT": (
        "HUMAN_REVIEW_IDENTIFIER_CONFLICT",
        ("stronger_source_backed_identity_identifier",),
    ),
    "MULTIPLE_REVIEW_CAUSES": (
        "HUMAN_REVIEW_MULTIPLE_CAUSES",
        ("resolve_each_source_backed_review_cause",),
    ),
}


def _load_provenance_index(paths: Iterable[str | Path]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for raw_path in paths:
        path = Path(raw_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "podium7.catalog-identity-golden.v1":
            raise ValueError(f"unsupported enrichment corpus source: {path}")
        version = payload.get("datasetVersion")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"datasetVersion is required: {path}")
        sources_raw = payload.get("sources")
        cases = payload.get("cases")
        if not isinstance(sources_raw, list) or not sources_raw:
            raise ValueError(f"source-backed dataset has no sources: {path}")
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"source-backed dataset has no cases: {path}")
        sources: dict[str, str] = {}
        for source in sources_raw:
            if not isinstance(source, dict):
                raise ValueError(f"source entry must be an object: {path}")
            source_id = source.get("id")
            locator = source.get("url")
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError(f"source id is required: {path}")
            if not isinstance(locator, str) or not locator.startswith("https://"):
                raise ValueError(f"source URL must be HTTPS: {path}")
            sources[source_id] = locator

        for case in cases:
            if not isinstance(case, dict):
                raise ValueError(f"case entry must be an object: {path}")
            case_id = case.get("id")
            source_ids_raw = case.get("sourceIds")
            if not isinstance(case_id, str) or not case_id.strip():
                raise ValueError(f"case id is required: {path}")
            if not isinstance(source_ids_raw, list) or not source_ids_raw:
                raise ValueError(f"case {case_id!r} has no sourceIds")
            source_ids = tuple(str(value) for value in source_ids_raw)
            try:
                source_locators = tuple(sources[source_id] for source_id in source_ids)
            except KeyError as exc:
                raise ValueError(f"case {case_id!r} references unknown source {exc.args[0]!r}") from exc
            for side in ("left", "right"):
                evidence_id = f"operational:{version}:{case_id}:{side}"
                if evidence_id in index:
                    raise ValueError(f"duplicate operational evidence id {evidence_id!r}")
                index[evidence_id] = {
                    "caseId": case_id,
                    "side": side,
                    "sourceIds": source_ids,
                    "sourceLocators": source_locators,
                }
    if not index:
        raise ValueError("enrichment corpus cannot be empty")
    return index


def build_source_backed_enrichment_work(
    store: CatalogStore,
    paths: Iterable[str | Path],
) -> dict[str, Any]:
    provenance = _load_provenance_index(paths)
    queue = CatalogReviewQueue(store)
    open_count = queue.count_open()
    if open_count > 100:
        raise ValueError("bounded enrichment work queue currently supports at most 100 open reviews")
    tasks = queue.open_tasks(limit=max(1, open_count))
    items: list[EvidenceEnrichmentWorkItem] = []
    blocked: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()

    for task in tasks:
        source_context = provenance.get(task.evidence_id)
        if source_context is None:
            blocked.append(
                {
                    "reviewId": task.id,
                    "evidenceId": task.evidence_id,
                    "cause": "MISSING_PROVENANCE_CONTEXT",
                    "disposition": "BLOCK_AND_INVESTIGATE",
                }
            )
            counts["MISSING_PROVENANCE_CONTEXT"] += 1
            continue

        candidates = set(task.candidate_vehicle_ids)
        reasons = sorted(
            {
                comparison.reason
                for comparison in task.comparisons
                if comparison.vehicle_id in candidates
                and comparison.outcome in {"MATCH", "REVIEW"}
            }
        )
        if not reasons:
            categories = {"UNKNOWN_REVIEW_CAUSE"}
        else:
            categories = {classify_review_reason(reason) for reason in reasons}

        if "UNKNOWN_REVIEW_CAUSE" in categories:
            cause = "UNKNOWN_REVIEW_CAUSE"
        elif len(categories) == 1:
            cause = next(iter(categories))
        else:
            cause = "MULTIPLE_REVIEW_CAUSES"
        counts[cause] += 1

        requirement = _REQUIREMENTS.get(cause)
        if requirement is None:
            blocked.append(
                {
                    "reviewId": task.id,
                    "evidenceId": task.evidence_id,
                    "caseId": source_context["caseId"],
                    "side": source_context["side"],
                    "cause": cause,
                    "disposition": "BLOCK_AND_INVESTIGATE",
                    "sourceIds": list(source_context["sourceIds"]),
                    "sourceLocators": list(source_context["sourceLocators"]),
                }
            )
            continue

        disposition, required_evidence = requirement
        items.append(
            EvidenceEnrichmentWorkItem(
                review_id=task.id,
                evidence_id=task.evidence_id,
                case_id=source_context["caseId"],
                side=source_context["side"],
                cause=cause,
                disposition=disposition,
                required_evidence=required_evidence,
                source_ids=source_context["sourceIds"],
                source_locators=source_context["sourceLocators"],
                candidate_vehicle_ids=task.candidate_vehicle_ids,
            )
        )

    return {
        "schema": "podium7.production-evidence-enrichment-work.v1",
        "summary": {
            "openReviews": len(tasks),
            "actionable": len(items),
            "blocked": len(blocked),
            "resolverPolicyChanges": 0,
        },
        "causeCounts": dict(sorted(counts.items())),
        "items": [item.to_payload() for item in items],
        "blockedItems": blocked,
    }


__all__ = [
    "EvidenceEnrichmentWorkItem",
    "build_source_backed_enrichment_work",
]
