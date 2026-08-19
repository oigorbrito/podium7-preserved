from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path

from .domain import AutomotiveIdentity, CandidateFact, EntityKind, RawEvidence, Source
from .export import export_entity_json
from .fusion import fuse_candidates
from .identity import MatchOutcome, resolve_pair
from .ingestion import ingest_vehicle_makes_models_json
from .persistence import EvidenceStore
from .web_extraction import extract_autoevolution_artega_gt


WEB_SOURCE_ID = "autoevolution-artega-gt-web"
WEB_SOURCE_LOCATOR = "https://www.autoevolution.com/cars/artega-gt-2010.html"


@dataclass(frozen=True)
class AcceptanceReport:
    identity_outcome: MatchOutcome
    sources: int
    raw_evidence: int
    canonical_facts: int
    conflicts: int
    exported_json: str


def _stable_id(prefix: str, material: str) -> str:
    return f"{prefix}:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:24]}"


def run_acceptance_slice(structured_json: str | Path, web_snapshot: str | Path) -> AcceptanceReport:
    structured_path = Path(structured_json)
    web_path = Path(web_snapshot)
    acquired_at = datetime(2026, 8, 19, tzinfo=timezone.utc)

    with EvidenceStore(":memory:") as store:
        ingest_vehicle_makes_models_json(store, structured_path, acquired_at=acquired_at)

        pointer = "/makes/0/models/0/generations/0/engines/0"
        structured_locator = (
            "https://github.com/gor3a/vehicle-makes-models/blob/main/"
            f"data/json/{structured_path.name}#{pointer}"
        )
        structured_entity_id = _stable_id("entity", structured_locator)
        structured_identity = store.get_entity(structured_entity_id)
        if structured_identity is None:
            raise RuntimeError("structured GT entity was not persisted")

        store.save_source(Source(WEB_SOURCE_ID, "autoevolution", WEB_SOURCE_LOCATOR))
        web_entity_id = _stable_id("entity", WEB_SOURCE_LOCATOR)
        web_evidence_id = _stable_id("evidence", WEB_SOURCE_LOCATOR)
        web_identity = AutomotiveIdentity(
            kind=EntityKind.POWERTRAIN,
            make="Artega",
            model="GT",
            generation="GT (2010)",
            powertrain="3.6L V6 6AT (300 HP)",
            year_from=2010,
            year_to=2012,
            external_identifiers=(WEB_SOURCE_LOCATOR,),
        )
        store.save_entity(web_entity_id, web_identity)
        store.save_raw_evidence(
            RawEvidence(
                id=web_evidence_id,
                source_id=WEB_SOURCE_ID,
                locator=WEB_SOURCE_LOCATOR,
                retrieved_at=acquired_at,
                acquisition_method="verified-web-snapshot",
                raw_content_ref=str(web_path),
            )
        )

        identity_decision = resolve_pair(structured_identity, web_identity)
        if identity_decision.outcome is not MatchOutcome.MATCH:
            raise RuntimeError(f"acceptance identity resolution failed: {identity_decision}")

        web_facts = extract_autoevolution_artega_gt(web_path.read_text(encoding="utf-8"))
        for fact in web_facts:
            store.save_candidate_fact(
                CandidateFact(
                    id=_stable_id("candidate", f"{web_evidence_id}|{fact.attribute}"),
                    entity_candidate_id=web_entity_id,
                    attribute=fact.attribute,
                    raw_value=fact.raw_value,
                    normalized_value=fact.normalized_value,
                    unit=fact.unit,
                    evidence_id=web_evidence_id,
                    extraction_method=fact.extraction_rule,
                    confidence=None,
                    normalization_rule=fact.normalization_rule,
                )
            )

        structured_candidates = {fact.attribute: fact for fact in store.candidates_for_entity(structured_entity_id)}
        web_candidates = {fact.attribute: fact for fact in store.candidates_for_entity(web_entity_id)}

        canonical_facts = []
        conflicts = []
        for attribute in sorted(set(structured_candidates).intersection(web_candidates)):
            result = fuse_candidates(
                structured_entity_id,
                [structured_candidates[attribute], web_candidates[attribute]],
            )
            if result.canonical_fact is not None:
                provenance_id = f"provenance:{result.canonical_fact.id}"
                store.save_canonical_fact(result.canonical_fact, provenance_id)
                canonical_facts.append(result.canonical_fact)
            if result.conflict is not None:
                store.save_conflict(result.conflict)
                conflicts.append(result.conflict)

        counts = store.snapshot_counts()
        exported = export_entity_json(structured_entity_id, structured_identity, canonical_facts, conflicts)
        return AcceptanceReport(
            identity_outcome=identity_decision.outcome,
            sources=counts["sources"],
            raw_evidence=counts["raw_evidence"],
            canonical_facts=counts["canonical_facts"],
            conflicts=counts["conflicts"],
            exported_json=exported,
        )
