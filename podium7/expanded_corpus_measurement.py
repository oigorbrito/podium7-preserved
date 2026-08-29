from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from .catalog import CatalogStore
from .catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from .catalog_provenance_audit import audit_catalog_provenance
from .catalog_quality import evaluate_identity_quality
from .catalog_review_cause import CatalogReviewCauseStore
from .identity_regression import (
    compare_identity_quality_to_baseline,
    load_identity_safety_baseline,
)
from .measurement_artifact import measurement_artifact_json


EXPANDED_CORPUS_MEASUREMENT_SCHEMA = "podium7.expanded-corpus-measurement.v1"


def _strict_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def _expanded_records(corpus_path: Path) -> tuple[dict[str, Any], ...]:
    corpus = _strict_object(corpus_path)
    base_path = corpus_path.resolve().parents[1] / str(corpus["baseCorpus"])
    base = _strict_object(base_path)
    records = [*base["records"], *corpus["additionalRecords"]]
    if len(records) != corpus["expected"]["total"]:
        raise ValueError("expanded corpus record count does not match manifest")
    return tuple(records)


def _input_contributions(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        source_id = record["source"]["id"]
        for field, value in record["vehicle"].items():
            if value is not None and value != []:
                counts[field][source_id] += 1
    return {
        field: dict(sorted(source_counts.items()))
        for field, source_counts in sorted(counts.items())
    }


def _canonical_candidate_contributions(store: CatalogStore) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    after_id: str | None = None
    while True:
        vehicle_ids = store.catalog_vehicle_ids_page(after_id=after_id, limit=100)
        if not vehicle_ids:
            break
        for vehicle_id in vehicle_ids:
            for fact in store.catalog_candidates_for_entity(vehicle_id):
                evidence = store.get_raw_evidence(fact.evidence_id)
                if evidence is None:
                    raise RuntimeError(f"candidate evidence disappeared: {fact.evidence_id}")
                counts[fact.attribute][evidence.source_id] += 1
        if len(vehicle_ids) < 100:
            break
        after_id = vehicle_ids[-1]
    return {
        field: dict(sorted(source_counts.items()))
        for field, source_counts in sorted(counts.items())
    }


def measure_expanded_corpus(
    corpus_path: str | Path,
    quality_paths: Iterable[str | Path],
) -> tuple[dict[str, Any], dict[str, Any]]:
    corpus_path = Path(corpus_path)
    quality_paths = tuple(Path(path) for path in quality_paths)
    if not quality_paths:
        raise ValueError("at least one independently labeled quality dataset is required")

    corpus_raw = corpus_path.read_bytes()
    records = _expanded_records(corpus_path)
    store = CatalogStore()
    report = ingest_catalog_batch(store, parse_catalog_batch_payload({"records": records}))
    provenance = audit_catalog_provenance(store)
    quality = evaluate_identity_quality(quality_paths)

    baseline_path = corpus_path.parent / "production_identity_safety_baseline_v3.json"
    baseline_raw = baseline_path.read_bytes()
    baseline = load_identity_safety_baseline(baseline_path)
    safety_comparison = compare_identity_quality_to_baseline(quality, baseline)

    review_store = CatalogReviewCauseStore(store)
    review_causes: Counter[str] = Counter()
    review_snapshots: list[dict[str, Any]] = []
    for item in report.results:
        if item.review_id is None:
            continue
        snapshot = review_store.get(item.review_id)
        if snapshot is None:
            raise RuntimeError(f"review cause snapshot missing: {item.review_id}")
        review_causes.update(snapshot.causes)
        review_snapshots.append(
            {
                "reviewId": snapshot.review_id,
                "classifierVersion": snapshot.classifier_version,
                "causes": list(snapshot.causes),
            }
        )

    conflict_rows = store._connection.execute(
        "SELECT id, attribute, reason, resolution_state FROM conflicts ORDER BY id"
    ).fetchall()
    conflicts = [
        {
            "id": row["id"],
            "attribute": row["attribute"],
            "reason": row["reason"],
            "resolutionState": row["resolution_state"],
        }
        for row in conflict_rows
    ]

    retained_identity_safety = {
        "baseline": {
            "name": baseline_path.name,
            "sha256": sha256(baseline_raw).hexdigest(),
            "bytes": len(baseline_raw),
            "baselineVersion": baseline["baselineVersion"],
        },
        "comparison": safety_comparison,
        "boundary": "Retained identity-safety comparison uses independently labeled identity quality and is not derived from operational action labels.",
    }

    operational = {
        "schema": "podium7.production-operational-measurement.v1",
        "measurementScope": "INTEGRATED_PROVENANCE_FIRST_CORPUS_V2",
        "corpus": {
            "name": corpus_path.name,
            "sha256": sha256(corpus_raw).hexdigest(),
            "bytes": len(corpus_raw),
            "evidenceClass": _strict_object(corpus_path)["evidenceClass"],
        },
        "summary": {
            "total": report.total,
            "created": report.created,
            "matched": report.matched,
            "review": report.review,
            "failed": report.failed,
        },
        "reviewLoad": {
            "openReviewTasks": report.review,
            "causes": dict(sorted(review_causes.items())),
            "snapshots": review_snapshots,
        },
        "sourceContribution": {
            "observedInputByFieldAndSource": _input_contributions(records),
            "canonicalCandidateWritesByFieldAndSource": _canonical_candidate_contributions(store),
            "boundary": "Observed input is not a canonical write. REVIEW observations remain outside canonical candidate writes until resolved.",
        },
        "explicitConflicts": {
            "count": len(conflicts),
            "items": conflicts,
            "disposition": "NO_EXPLICIT_CONFLICTS" if not conflicts else "EXPLICIT_CONFLICTS_RETAINED",
        },
        "provenance": provenance,
        "retainedIdentitySafety": retained_identity_safety,
    }

    artifact_json = measurement_artifact_json(
        quality_paths,
        identity_quality=quality,
        operational=operational,
    )
    artifact = json.loads(artifact_json)
    measurement = {
        "schema": EXPANDED_CORPUS_MEASUREMENT_SCHEMA,
        "operational": operational,
        "labeledIdentityQuality": quality,
        "retainedIdentitySafety": retained_identity_safety,
        "artifact": artifact,
        "boundaries": {
            "precisionRecallBasis": "independently labeled identity benchmark cases only",
            "operationalActionsAreQualityLabels": False,
            "historicalV3BlockedSidesIncluded": False,
            "productionCompletenessClaim": False,
        },
    }
    return measurement, artifact


__all__ = ["EXPANDED_CORPUS_MEASUREMENT_SCHEMA", "measure_expanded_corpus"]
