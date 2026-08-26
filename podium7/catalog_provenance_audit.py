from __future__ import annotations

from typing import Any

from .catalog import CatalogStore
from .catalog_api import lookup_catalog_vehicle
from .catalog_review import CatalogReviewQueue


def audit_catalog_provenance(store: CatalogStore) -> dict[str, Any]:
    incomplete: list[dict[str, str]] = []
    checked_links = 0
    complete_links = 0

    vehicle_ids = store.catalog_vehicle_ids_page(limit=100)
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

    review_queue = CatalogReviewQueue(store)
    for task in review_queue.open_tasks(limit=100):
        checked_links += 1
        evidence = store.get_raw_evidence(task.evidence_id)
        if evidence is None:
            incomplete.append({"kind": "REVIEW_MISSING_EVIDENCE", "reviewId": task.id})
            continue
        complete_links += 1

        checked_links += 1
        source = store.get_source(evidence.source_id)
        if source is None:
            incomplete.append({"kind": "REVIEW_EVIDENCE_MISSING_SOURCE", "reviewId": task.id})
        else:
            complete_links += 1

    return {
        "schema": "podium7.catalog-provenance-audit.v1",
        "summary": {
            "catalogVehicles": len(vehicle_ids),
            "openReviewTasks": review_queue.count_open(),
            "checkedLinks": checked_links,
            "completeLinks": complete_links,
            "incompleteLinks": len(incomplete),
            "completeness": 1.0 if checked_links == 0 else complete_links / checked_links,
            "pass": not incomplete,
        },
        "incomplete": incomplete,
    }


__all__ = ["audit_catalog_provenance"]
