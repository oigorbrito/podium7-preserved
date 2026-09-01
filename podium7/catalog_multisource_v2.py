from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .catalog_ingestion import catalog_identity_from_record
from .domain import RawEvidence, Source


CATALOG_MULTISOURCE_V2_CONTRACT = "podium7.catalog-operational.v2"


class CatalogMultisourceV2Error(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class CatalogMultisourceV2Envelope:
    contract_version: str
    record_id: str
    vehicle: dict[str, Any]
    sources: tuple[Source, ...]
    evidence: tuple[RawEvidence, ...]
    field_evidence: tuple[tuple[str, tuple[str, ...]], ...]

    def evidence_ids_for_field(self, field_name: str) -> tuple[str, ...]:
        for name, evidence_ids in self.field_evidence:
            if name == field_name:
                return evidence_ids
        raise KeyError(field_name)


def _fail(code: str, message: str) -> None:
    raise CatalogMultisourceV2Error(code, message)


def _required_text(payload: Mapping[str, Any], key: str, path: str, code: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        _fail(code, f"{path}.{key} must be non-empty text")
    return value.strip()


def _required_object(payload: Mapping[str, Any], key: str, path: str, code: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        _fail(code, f"{path}.{key} must be an object")
    return value


def _required_array(payload: Mapping[str, Any], key: str, path: str, code: str) -> Sequence[Any]:
    value = payload.get(key)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        _fail(code, f"{path}.{key} must be a non-empty array")
    return value


def _reject_unknown(payload: Mapping[str, Any], allowed: set[str], path: str, code: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        _fail(code, f"{path} has unsupported fields: " + ", ".join(unknown))


def _timestamp(value: str, path: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise CatalogMultisourceV2Error(
            "INVALID_EVIDENCE",
            f"{path} must be an ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail("INVALID_EVIDENCE", f"{path} must include a timezone")
    return parsed


def _parse_sources(items: Sequence[Any], path: str) -> tuple[Source, ...]:
    sources: list[Source] = []
    seen: set[str] = set()
    for index, raw in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(raw, Mapping):
            _fail("INVALID_SOURCE", f"{item_path} must be an object")
        _reject_unknown(raw, {"id", "name", "locator"}, item_path, "INVALID_SOURCE")
        source = Source(
            id=_required_text(raw, "id", item_path, "INVALID_SOURCE"),
            name=_required_text(raw, "name", item_path, "INVALID_SOURCE"),
            locator=_required_text(raw, "locator", item_path, "INVALID_SOURCE"),
        )
        if source.id in seen:
            _fail("DUPLICATE_SOURCE_ID", f"duplicate source id: {source.id}")
        seen.add(source.id)
        sources.append(source)
    return tuple(sorted(sources, key=lambda item: item.id))


def _parse_evidence(
    items: Sequence[Any],
    source_ids: set[str],
    path: str,
) -> tuple[RawEvidence, ...]:
    evidence_items: list[RawEvidence] = []
    seen: set[str] = set()
    for index, raw in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(raw, Mapping):
            _fail("INVALID_EVIDENCE", f"{item_path} must be an object")
        _reject_unknown(
            raw,
            {"id", "sourceId", "locator", "retrievedAt", "acquisitionMethod", "rawContentRef"},
            item_path,
            "INVALID_EVIDENCE",
        )
        evidence_id = _required_text(raw, "id", item_path, "INVALID_EVIDENCE")
        if evidence_id in seen:
            _fail("DUPLICATE_EVIDENCE_ID", f"duplicate evidence id: {evidence_id}")
        source_id = _required_text(raw, "sourceId", item_path, "INVALID_EVIDENCE")
        if source_id not in source_ids:
            _fail(
                "UNKNOWN_EVIDENCE_SOURCE",
                f"{item_path}.sourceId references undeclared source {source_id!r}",
            )
        seen.add(evidence_id)
        evidence_items.append(
            RawEvidence(
                id=evidence_id,
                source_id=source_id,
                locator=_required_text(raw, "locator", item_path, "INVALID_EVIDENCE"),
                retrieved_at=_timestamp(
                    _required_text(raw, "retrievedAt", item_path, "INVALID_EVIDENCE"),
                    f"{item_path}.retrievedAt",
                ),
                acquisition_method=_required_text(
                    raw,
                    "acquisitionMethod",
                    item_path,
                    "INVALID_EVIDENCE",
                ),
                raw_content_ref=_required_text(
                    raw,
                    "rawContentRef",
                    item_path,
                    "INVALID_EVIDENCE",
                ),
            )
        )
    return tuple(sorted(evidence_items, key=lambda item: item.id))


def _present_vehicle_fields(vehicle_payload: Mapping[str, Any]) -> set[str]:
    identity = catalog_identity_from_record(vehicle_payload)
    fields: set[str] = set()
    for field_name in vehicle_payload:
        value = getattr(identity, field_name)
        if value is None:
            continue
        if isinstance(value, tuple) and not value:
            continue
        fields.add(field_name)
    return fields


def _parse_field_evidence(
    raw: Mapping[str, Any],
    present_fields: set[str],
    evidence_ids: set[str],
    path: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    raw_fields = set(raw)
    missing = sorted(present_fields - raw_fields)
    if missing:
        _fail(
            "MISSING_FIELD_EVIDENCE",
            f"{path} is missing bindings for: " + ", ".join(missing),
        )
    extraneous = sorted(raw_fields - present_fields)
    if extraneous:
        _fail(
            "EXTRANEOUS_FIELD_EVIDENCE",
            f"{path} binds absent fields: " + ", ".join(extraneous),
        )

    normalized: list[tuple[str, tuple[str, ...]]] = []
    for field_name in sorted(present_fields):
        refs = raw[field_name]
        if isinstance(refs, (str, bytes)) or not isinstance(refs, Sequence) or not refs:
            _fail(
                "EMPTY_FIELD_EVIDENCE",
                f"{path}.{field_name} must be a non-empty array of evidence ids",
            )
        parsed_refs: list[str] = []
        seen: set[str] = set()
        for ref in refs:
            if not isinstance(ref, str) or not ref.strip():
                _fail(
                    "UNKNOWN_FIELD_EVIDENCE",
                    f"{path}.{field_name} contains an invalid evidence id",
                )
            evidence_id = ref.strip()
            if evidence_id in seen:
                _fail(
                    "DUPLICATE_FIELD_EVIDENCE",
                    f"{path}.{field_name} repeats evidence id {evidence_id!r}",
                )
            if evidence_id not in evidence_ids:
                _fail(
                    "UNKNOWN_FIELD_EVIDENCE",
                    f"{path}.{field_name} references undeclared evidence {evidence_id!r}",
                )
            seen.add(evidence_id)
            parsed_refs.append(evidence_id)
        normalized.append((field_name, tuple(sorted(parsed_refs))))
    return tuple(normalized)


def parse_catalog_multisource_v2_record(payload: Any) -> CatalogMultisourceV2Envelope:
    if not isinstance(payload, Mapping):
        _fail("INVALID_RECORD", "record must be an object")
    _reject_unknown(
        payload,
        {"contractVersion", "recordId", "vehicle", "provenance"},
        "$",
        "INVALID_RECORD",
    )

    contract_version = payload.get("contractVersion")
    if contract_version != CATALOG_MULTISOURCE_V2_CONTRACT:
        _fail(
            "UNSUPPORTED_CONTRACT_VERSION",
            f"$.contractVersion must be {CATALOG_MULTISOURCE_V2_CONTRACT!r}",
        )
    record_id = _required_text(payload, "recordId", "$", "INVALID_RECORD_ID")

    vehicle_payload = _required_object(payload, "vehicle", "$", "INVALID_VEHICLE")
    try:
        present_fields = _present_vehicle_fields(vehicle_payload)
    except (TypeError, ValueError) as exc:
        raise CatalogMultisourceV2Error("INVALID_VEHICLE", str(exc)) from exc
    if not present_fields:
        _fail("INVALID_VEHICLE", "$.vehicle must contain at least one present field")

    provenance = _required_object(payload, "provenance", "$", "INVALID_PROVENANCE")
    _reject_unknown(
        provenance,
        {"sources", "evidence", "fieldEvidence"},
        "$.provenance",
        "INVALID_PROVENANCE",
    )
    source_items = _required_array(provenance, "sources", "$.provenance", "MISSING_SOURCES")
    evidence_items = _required_array(
        provenance,
        "evidence",
        "$.provenance",
        "MISSING_EVIDENCE",
    )
    field_evidence_payload = _required_object(
        provenance,
        "fieldEvidence",
        "$.provenance",
        "MISSING_FIELD_EVIDENCE",
    )

    sources = _parse_sources(source_items, "$.provenance.sources")
    evidence = _parse_evidence(
        evidence_items,
        {source.id for source in sources},
        "$.provenance.evidence",
    )
    field_evidence = _parse_field_evidence(
        field_evidence_payload,
        present_fields,
        {item.id for item in evidence},
        "$.provenance.fieldEvidence",
    )

    return CatalogMultisourceV2Envelope(
        contract_version=CATALOG_MULTISOURCE_V2_CONTRACT,
        record_id=record_id,
        vehicle=dict(vehicle_payload),
        sources=sources,
        evidence=evidence,
        field_evidence=field_evidence,
    )


__all__ = [
    "CATALOG_MULTISOURCE_V2_CONTRACT",
    "CatalogMultisourceV2Envelope",
    "CatalogMultisourceV2Error",
    "parse_catalog_multisource_v2_record",
]
