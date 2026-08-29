from __future__ import annotations

from typing import Any

from .catalog import CatalogStore, export_catalog_vehicle_payload


TRACE_BUNDLE_SCHEMA = "podium7.catalog-evidence-trace-bundle.v1"


def catalog_evidence_trace(store: CatalogStore, vehicle_id: str) -> list[dict[str, Any]]:
    """Return deterministic persisted candidate -> evidence -> source trace entries."""
    canonical = store.resolve_catalog_id(vehicle_id)
    if store.get_catalog_vehicle(canonical) is None:
        raise ValueError("catalog vehicle does not exist")

    candidates = store.catalog_candidates_for_entity(canonical)
    if not candidates:
        raise ValueError("catalog vehicle has no persisted candidate evidence")

    entries: list[dict[str, Any]] = []
    for candidate in candidates:
        evidence = store.get_raw_evidence(candidate.evidence_id)
        if evidence is None:
            raise ValueError(
                f"catalog candidate {candidate.id!r} references missing evidence {candidate.evidence_id!r}"
            )
        source = store.get_source(evidence.source_id)
        if source is None:
            raise ValueError(
                f"catalog evidence {evidence.id!r} references missing source {evidence.source_id!r}"
            )
        entries.append(
            {
                "candidateFactId": candidate.id,
                "attribute": candidate.attribute,
                "evidenceId": evidence.id,
                "sourceId": source.id,
                "evidenceLocator": evidence.locator,
                "sourceLocator": source.locator,
                "rawContentRef": evidence.raw_content_ref,
                "extractionMethod": candidate.extraction_method,
                "normalizationRule": candidate.normalization_rule,
            }
        )
    return sorted(
        entries,
        key=lambda item: (
            item["attribute"],
            item["candidateFactId"],
            item["evidenceId"],
            item["sourceId"],
        ),
    )


def export_catalog_vehicle_evidence_bundle(
    store: CatalogStore,
    vehicle_id: str,
    *,
    contract_version: str,
) -> dict[str, Any]:
    """Return an opt-in provenance bundle without changing the frozen vehicle wire contract."""
    return {
        "schema": TRACE_BUNDLE_SCHEMA,
        "vehicle": export_catalog_vehicle_payload(
            store,
            vehicle_id,
            contract_version=contract_version,
        ),
        "evidenceTrace": catalog_evidence_trace(store, vehicle_id),
    }


__all__ = [
    "TRACE_BUNDLE_SCHEMA",
    "catalog_evidence_trace",
    "export_catalog_vehicle_evidence_bundle",
]
