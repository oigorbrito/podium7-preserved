from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .catalog import CatalogVehicleIdentity
from .catalog_ingestion import catalog_identity_from_record
from .domain import RawEvidence, Source


CATALOG_OPERATIONAL_V2 = "podium7.catalog-operational.v2"

UNSUPPORTED_CONTRACT_VERSION = "UNSUPPORTED_CONTRACT_VERSION"
INVALID_RECORD_ID = "INVALID_RECORD_ID"
INVALID_VEHICLE = "INVALID_VEHICLE"
MISSING_SOURCES = "MISSING_SOURCES"
INVALID_SOURCE = "INVALID_SOURCE"
DUPLICATE_SOURCE_ID = "DUPLICATE_SOURCE_ID"
MISSING_EVIDENCE = "MISSING_EVIDENCE"
INVALID_EVIDENCE = "INVALID_EVIDENCE"
DUPLICATE_EVIDENCE_ID = "DUPLICATE_EVIDENCE_ID"
UNKNOWN_EVIDENCE_SOURCE = "UNKNOWN_EVIDENCE_SOURCE"
MISSING_FIELD_EVIDENCE = "MISSING_FIELD_EVIDENCE"
INVALID_FIELD_EVIDENCE = "INVALID_FIELD_EVIDENCE"
EXTRANEOUS_FIELD_EVIDENCE = "EXTRANEOUS_FIELD_EVIDENCE"
EMPTY_FIELD_EVIDENCE = "EMPTY_FIELD_EVIDENCE"
UNKNOWN_FIELD_EVIDENCE = "UNKNOWN_FIELD_EVIDENCE"
DUPLICATE_FIELD_EVIDENCE = "DUPLICATE_FIELD_EVIDENCE"


class CatalogOperationalV2Error(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CatalogOperationalV2Envelope:
    record_id: str
    vehicle: CatalogVehicleIdentity
    sources: tuple[Source, ...]
    evidence: tuple[RawEvidence, ...]
    field_evidence: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def field_evidence_map(self) -> dict[str, tuple[str, ...]]:
        return dict(self.field_evidence)


def _error(code: str, message: str) -> CatalogOperationalV2Error:
    return CatalogOperationalV2Error(code, message)


def _is_sequence(value: Any) -> bool:
    return not isinstance(value, (str, bytes)) and isinstance(value, Sequence)


def _required_text(payload: Mapping[str, Any], key: str, *, code: str, path: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise _error(code, f"{path}.{key} must be non-empty text")
    return value.strip()


def _reject_unknown(payload: Mapping[str, Any], allowed: set[str], *, code: str, path: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise _error(code, f"{path} has unsupported fields: " + ", ".join(unknown))


def _timestamp(value: Any, *, path: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise _error(INVALID_EVIDENCE, f"{path} must be an ISO-8601 timestamp")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise _error(INVALID_EVIDENCE, f"{path} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _error(INVALID_EVIDENCE, f"{path} must include a timezone")
    return parsed


def _present_vehicle_fields(identity: CatalogVehicleIdentity) -> set[str]:
    payload = asdict(identity)
    present: set[str] = set()
    for field, value in payload.items():
        if value is None:
            continue
        if field in {"aliases", "engine_identifiers", "external_identifiers"} and not value:
            continue
        present.add(field)
    return present


def _parse_sources(provenance: Mapping[str, Any]) -> tuple[Source, ...]:
    raw_sources = provenance.get("sources")
    if not _is_sequence(raw_sources) or not raw_sources:
        raise _error(MISSING_SOURCES, "$.provenance.sources must be a non-empty array")

    sources: list[Source] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_sources):
        path = f"$.provenance.sources[{index}]"
        if not isinstance(raw, Mapping):
            raise _error(INVALID_SOURCE, f"{path} must be an object")
        _reject_unknown(raw, {"id", "name", "locator"}, code=INVALID_SOURCE, path=path)
        source_id = _required_text(raw, "id", code=INVALID_SOURCE, path=path)
        if source_id in seen:
            raise _error(DUPLICATE_SOURCE_ID, f"duplicate source id: {source_id}")
        seen.add(source_id)
        sources.append(
            Source(
                id=source_id,
                name=_required_text(raw, "name", code=INVALID_SOURCE, path=path),
                locator=_required_text(raw, "locator", code=INVALID_SOURCE, path=path),
            )
        )
    return tuple(sorted(sources, key=lambda item: item.id))


def _parse_evidence(
    provenance: Mapping[str, Any],
    source_ids: set[str],
) -> tuple[RawEvidence, ...]:
    raw_evidence = provenance.get("evidence")
    if not _is_sequence(raw_evidence) or not raw_evidence:
        raise _error(MISSING_EVIDENCE, "$.provenance.evidence must be a non-empty array")

    evidence: list[RawEvidence] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_evidence):
        path = f"$.provenance.evidence[{index}]"
        if not isinstance(raw, Mapping):
            raise _error(INVALID_EVIDENCE, f"{path} must be an object")
        _reject_unknown(
            raw,
            {"id", "sourceId", "locator", "retrievedAt", "acquisitionMethod", "rawContentRef"},
            code=INVALID_EVIDENCE,
            path=path,
        )
        evidence_id = _required_text(raw, "id", code=INVALID_EVIDENCE, path=path)
        if evidence_id in seen:
            raise _error(DUPLICATE_EVIDENCE_ID, f"duplicate evidence id: {evidence_id}")
        seen.add(evidence_id)
        source_id = _required_text(raw, "sourceId", code=INVALID_EVIDENCE, path=path)
        if source_id not in source_ids:
            raise _error(
                UNKNOWN_EVIDENCE_SOURCE,
                f"{path}.sourceId references undeclared source: {source_id}",
            )
        evidence.append(
            RawEvidence(
                id=evidence_id,
                source_id=source_id,
                locator=_required_text(raw, "locator", code=INVALID_EVIDENCE, path=path),
                retrieved_at=_timestamp(raw.get("retrievedAt"), path=f"{path}.retrievedAt"),
                acquisition_method=_required_text(
                    raw, "acquisitionMethod", code=INVALID_EVIDENCE, path=path
                ),
                raw_content_ref=_required_text(
                    raw, "rawContentRef", code=INVALID_EVIDENCE, path=path
                ),
            )
        )
    return tuple(sorted(evidence, key=lambda item: item.id))


def _parse_field_evidence(
    provenance: Mapping[str, Any],
    *,
    present_fields: set[str],
    evidence_ids: set[str],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    raw_bindings = provenance.get("fieldEvidence")
    if not isinstance(raw_bindings, Mapping):
        raise _error(MISSING_FIELD_EVIDENCE, "$.provenance.fieldEvidence must be an object")

    fields = set(raw_bindings)
    missing = sorted(present_fields - fields)
    if missing:
        raise _error(
            MISSING_FIELD_EVIDENCE,
            "missing fieldEvidence for present fields: " + ", ".join(missing),
        )
    extra = sorted(fields - present_fields)
    if extra:
        raise _error(
            EXTRANEOUS_FIELD_EVIDENCE,
            "fieldEvidence names absent vehicle fields: " + ", ".join(extra),
        )

    normalized: list[tuple[str, tuple[str, ...]]] = []
    for field in sorted(present_fields):
        refs = raw_bindings[field]
        if not _is_sequence(refs):
            raise _error(
                INVALID_FIELD_EVIDENCE,
                f"$.provenance.fieldEvidence.{field} must be an array",
            )
        if not refs:
            raise _error(
                EMPTY_FIELD_EVIDENCE,
                f"$.provenance.fieldEvidence.{field} must contain evidence ids",
            )
        if any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            raise _error(
                INVALID_FIELD_EVIDENCE,
                f"$.provenance.fieldEvidence.{field} must contain non-empty evidence ids",
            )
        cleaned = tuple(ref.strip() for ref in refs)
        if len(cleaned) != len(set(cleaned)):
            raise _error(
                DUPLICATE_FIELD_EVIDENCE,
                f"$.provenance.fieldEvidence.{field} contains duplicate evidence ids",
            )
        unknown = sorted(set(cleaned) - evidence_ids)
        if unknown:
            raise _error(
                UNKNOWN_FIELD_EVIDENCE,
                f"$.provenance.fieldEvidence.{field} references undeclared evidence: "
                + ", ".join(unknown),
            )
        normalized.append((field, tuple(sorted(cleaned))))
    return tuple(normalized)


def parse_catalog_operational_v2(payload: Any) -> CatalogOperationalV2Envelope:
    if not isinstance(payload, Mapping):
        raise _error(UNSUPPORTED_CONTRACT_VERSION, "$ must be an object")
    _reject_unknown(
        payload,
        {"contractVersion", "recordId", "vehicle", "provenance"},
        code=UNSUPPORTED_CONTRACT_VERSION,
        path="$",
    )
    if payload.get("contractVersion") != CATALOG_OPERATIONAL_V2:
        raise _error(
            UNSUPPORTED_CONTRACT_VERSION,
            f"$.contractVersion must be {CATALOG_OPERATIONAL_V2!r}",
        )
    record_id = _required_text(payload, "recordId", code=INVALID_RECORD_ID, path="$")

    raw_vehicle = payload.get("vehicle")
    if not isinstance(raw_vehicle, Mapping):
        raise _error(INVALID_VEHICLE, "$.vehicle must be an object")
    try:
        vehicle = catalog_identity_from_record(raw_vehicle)
    except (TypeError, ValueError) as exc:
        raise _error(INVALID_VEHICLE, str(exc)) from exc

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise _error(MISSING_SOURCES, "$.provenance must be an object")
    _reject_unknown(
        provenance,
        {"sources", "evidence", "fieldEvidence"},
        code=INVALID_FIELD_EVIDENCE,
        path="$.provenance",
    )

    sources = _parse_sources(provenance)
    evidence = _parse_evidence(provenance, {item.id for item in sources})
    field_evidence = _parse_field_evidence(
        provenance,
        present_fields=_present_vehicle_fields(vehicle),
        evidence_ids={item.id for item in evidence},
    )
    return CatalogOperationalV2Envelope(
        record_id=record_id,
        vehicle=vehicle,
        sources=sources,
        evidence=evidence,
        field_evidence=field_evidence,
    )


__all__ = [
    "CATALOG_OPERATIONAL_V2",
    "CatalogOperationalV2Envelope",
    "CatalogOperationalV2Error",
    "DUPLICATE_EVIDENCE_ID",
    "DUPLICATE_FIELD_EVIDENCE",
    "DUPLICATE_SOURCE_ID",
    "EMPTY_FIELD_EVIDENCE",
    "EXTRANEOUS_FIELD_EVIDENCE",
    "INVALID_EVIDENCE",
    "INVALID_FIELD_EVIDENCE",
    "INVALID_RECORD_ID",
    "INVALID_SOURCE",
    "INVALID_VEHICLE",
    "MISSING_EVIDENCE",
    "MISSING_FIELD_EVIDENCE",
    "MISSING_SOURCES",
    "UNKNOWN_EVIDENCE_SOURCE",
    "UNKNOWN_FIELD_EVIDENCE",
    "UNSUPPORTED_CONTRACT_VERSION",
    "parse_catalog_operational_v2",
]
