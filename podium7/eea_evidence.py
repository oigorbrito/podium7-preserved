from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
from typing import Any

from .domain import CandidateFact, RawEvidence
from .eea_source import EeaRecordReport, extract_eea_response


EEA_SOURCE_ID = "eea_co2_cars"
EEA_EXTRACTION_METHOD = "eea.co2_cars.regulatory_evidence.v1"


@dataclass(frozen=True)
class EeaEvidenceRecord:
    evidence: RawEvidence
    source_record_id: int
    facts: tuple[CandidateFact, ...]
    report: EeaRecordReport


def _require_content_ref(raw_payload: bytes, raw_content_ref: str) -> str:
    digest = hashlib.sha256(raw_payload).hexdigest()
    prefix = f"sha256:{digest}@"
    if not isinstance(raw_content_ref, str) or not raw_content_ref.startswith(prefix):
        raise ValueError("raw_content_ref must address the exact EEA response bytes")
    retained_location = raw_content_ref[len(prefix):]
    if not retained_location.strip():
        raise ValueError("raw_content_ref must retain a snapshot location")
    return digest


def _fact(*, evidence_id: str, entity_candidate_id: str, source_record_id: int, attribute: str, raw_value: Any, normalized_value: Any, unit: str | None = None) -> CandidateFact:
    return CandidateFact(
        id=f"{evidence_id}:{source_record_id}:{attribute}",
        entity_candidate_id=entity_candidate_id,
        attribute=attribute,
        raw_value=raw_value,
        normalized_value=normalized_value,
        unit=unit,
        evidence_id=evidence_id,
        extraction_method=EEA_EXTRACTION_METHOD,
        confidence=None,
        normalization_rule="eea:explicit-source-semantics:v1",
    )


def parse_eea_evidence(raw_payload: bytes, *, locator: str, retrieved_at: datetime, raw_content_ref: str, entity_candidate_ids: dict[int, str]) -> tuple[EeaEvidenceRecord, ...]:
    if not isinstance(raw_payload, bytes) or not raw_payload:
        raise ValueError("raw_payload must be non-empty bytes")
    if not isinstance(locator, str) or not locator.startswith("https://discodata.eea.europa.eu/"):
        raise ValueError("locator must be an HTTPS EEA Discodata locator")
    if not isinstance(retrieved_at, datetime) or retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
        raise ValueError("retrieved_at must be timezone-aware")
    if not isinstance(entity_candidate_ids, dict) or not entity_candidate_ids:
        raise ValueError("entity_candidate_ids are required")
    if any(isinstance(record_id, bool) or not isinstance(record_id, int) for record_id in entity_candidate_ids):
        raise ValueError("entity_candidate_ids keys must be integer EEA record ids")
    if any(not isinstance(candidate_id, str) or not candidate_id.strip() for candidate_id in entity_candidate_ids.values()):
        raise ValueError("entity_candidate_ids values must be non-empty candidate ids")

    digest = _require_content_ref(raw_payload, raw_content_ref)
    evidence_id = f"eea-co2-cars:{digest}"
    evidence = RawEvidence(id=evidence_id, source_id=EEA_SOURCE_ID, locator=locator, retrieved_at=retrieved_at, acquisition_method="bounded_structured_dataset", raw_content_ref=raw_content_ref)

    try:
        reports = extract_eea_response(raw_payload)
    except ValueError as exc:
        message = str(exc)
        if message.startswith("duplicate EEA source record ID "):
            suffix = message[len("duplicate EEA source record ID ") :]
            raise ValueError(f"duplicate EEA source record id {suffix}") from exc
        raise
    output: list[EeaEvidenceRecord] = []
    observed_ids: set[int] = set()
    for report in reports:
        identity = report.identity
        record_id = identity.source_record_id
        if record_id in observed_ids:
            raise ValueError(f"duplicate EEA source record id {record_id}")
        if report.issues:
            codes = ", ".join(issue.code for issue in report.issues)
            raise ValueError(f"EEA record {record_id} has incomplete or unsupported evidence: {codes}")
        candidate_id = entity_candidate_ids.get(record_id)
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError(f"missing entity candidate binding for EEA record {record_id}")
        candidate_id = candidate_id.strip()
        observed_ids.add(record_id)
        facts: list[CandidateFact] = [
            _fact(evidence_id=evidence_id, entity_candidate_id=candidate_id, source_record_id=record_id, attribute="make", raw_value=identity.make, normalized_value=identity.make),
            _fact(evidence_id=evidence_id, entity_candidate_id=candidate_id, source_record_id=record_id, attribute="model", raw_value=identity.commercial_name, normalized_value=identity.commercial_name),
            _fact(evidence_id=evidence_id, entity_candidate_id=candidate_id, source_record_id=record_id, attribute="eea.registration_year", raw_value=identity.registration_year, normalized_value=identity.registration_year),
        ]
        for attribute, value in (("eea.type_approval_number", identity.type_approval_number), ("eea.vehicle_type", identity.vehicle_type), ("eea.variant", identity.variant), ("eea.version", identity.version)):
            if value is not None:
                facts.append(_fact(evidence_id=evidence_id, entity_candidate_id=candidate_id, source_record_id=record_id, attribute=attribute, raw_value=value, normalized_value=value))
        for extracted in report.facts:
            facts.append(_fact(evidence_id=evidence_id, entity_candidate_id=candidate_id, source_record_id=record_id, attribute=extracted.attribute, raw_value=extracted.raw_value, normalized_value=extracted.normalized_value, unit=extracted.unit))
        output.append(EeaEvidenceRecord(evidence=evidence, source_record_id=record_id, facts=tuple(facts), report=report))

    extra_bindings = sorted(set(entity_candidate_ids) - observed_ids)
    if extra_bindings:
        raise ValueError("entity candidate bindings reference absent EEA records: " + ", ".join(map(str, extra_bindings)))
    return tuple(output)


__all__ = ["EEA_EXTRACTION_METHOD", "EEA_SOURCE_ID", "EeaEvidenceRecord", "parse_eea_evidence"]
