from __future__ import annotations

from typing import Any

from .catalog import CatalogStore
from .catalog_api import lookup_catalog_vehicle
from .catalog_review import CatalogReviewQueue, CatalogReviewState


def _all_catalog_vehicle_ids(store: CatalogStore, *, page_size: int = 100) -> list[str]:
    vehicle_ids: list[str] = []
    after_id: str | None = None
    while True:
        page = store.catalog_vehicle_ids_page(after_id=after_id, limit=page_size)
        if not page:
            return vehicle_ids
        vehicle_ids.extend(page)
        if len(page) < page_size:
            return vehicle_ids
        after_id = page[-1]


def audit_catalog_provenance(store: CatalogStore) -> dict[str, Any]:
    incomplete: list[dict[str, str]] = []
    checked_links = 0
    complete_links = 0

    vehicle_ids = _all_catalog_vehicle_ids(store)
    for vehicle_id in vehicle_ids:
        candidates = store.catalog_candidates_for_entity(vehicle_id)
        checked_links += 1
        if not candidates:
            incomplete.append({"kind": "CANONICAL_WITHOUT_CANDIDATE", "vehicleId": vehicle_id})
        else:
            complete_links += 1

        for candidate in candidates:
            checked_links += 1
            evidence = store.get_raw_evidence(candidate.evidence_id)
            if evidence is None:
                incomplete.append({"kind": "CANDIDATE_MISSING_EVIDENCE", "candidateId": candidate.id})
                continue
            complete_links += 1

            checked_links += 1
            source = store.get_source(evidence.source_id)
            if source is None:
                incomplete.append({"kind": "EVIDENCE_MISSING_SOURCE", "evidenceId": evidence.id})
            else:
                complete_links += 1

        checked_links += 1
        consumer = lookup_catalog_vehicle(store, vehicle_id)
        if not consumer.get("ok") or consumer.get("canonicalId") != vehicle_id:
            incomplete.append({"kind": "CANONICAL_CONSUMER_MISMATCH", "vehicleId": vehicle_id})
        else:
            complete_links += 1

    CatalogReviewQueue(store)
    open_review_rows = store._connection.execute(
        """
        SELECT id, evidence_id
        FROM catalog_v2_review_tasks
        WHERE state = ?
        ORDER BY created_at, id
        """,
        (CatalogReviewState.OPEN.value,),
    ).fetchall()
    for row in open_review_rows:
        review_id = row["id"]
        evidence_id = row["evidence_id"]
        checked_links += 1
        evidence = store.get_raw_evidence(evidence_id)
        if evidence is None:
            incomplete.append({"kind": "REVIEW_MISSING_EVIDENCE", "reviewId": review_id})
            continue
        complete_links += 1

        checked_links += 1
        source = store.get_source(evidence.source_id)
        if source is None:
            incomplete.append({"kind": "REVIEW_EVIDENCE_MISSING_SOURCE", "reviewId": review_id})
        else:
            complete_links += 1

    if checked_links == 0:
        incomplete.append({"kind": "EMPTY_AUDIT_SCOPE"})

    return {
        "schema": "podium7.catalog-provenance-audit.v1",
        "summary": {
            "catalogVehicles": len(vehicle_ids),
            "openReviewTasks": len(open_review_rows),
            "checkedLinks": checked_links,
            "completeLinks": complete_links,
            "incompleteLinks": len(incomplete),
            "completeness": 0.0 if checked_links == 0 else complete_links / checked_links,
            "pass": not incomplete,
        },
        "incomplete": incomplete,
    }


__all__ = ["audit_catalog_provenance"]
