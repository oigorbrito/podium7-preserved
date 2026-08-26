from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any
from urllib.parse import quote

from .domain import CandidateFact, RawEvidence


NHTSA_VPIC_SOURCE_ID = "nhtsa_vpic"
NHTSA_VPIC_EXTRACTION_METHOD = "nhtsa_vpic.decode_vin_values.v1"
_RAW_REF_PATTERN = re.compile(r"^sha256:([0-9a-f]{64})@(.+)$")
_ALLOWED_DECODE_ERROR_CODES = frozenset({"0", "6"})
_FIELD_MAP: dict[str, tuple[str, str]] = {
    "Make": ("make", "text"),
    "MakeID": ("nhtsa.make_id", "int"),
    "Model": ("model", "text"),
    "ModelID": ("nhtsa.model_id", "int"),
    "ModelYear": ("model_year", "int"),
    "BodyClass": ("nhtsa.body_class", "text"),
    "Trim": ("nhtsa.trim", "text"),
    "Series": ("nhtsa.series", "text"),
    "EngineModel": ("nhtsa.engine_model", "text"),
    "TransmissionStyle": ("nhtsa.transmission_style", "text"),
    "FuelTypePrimary": ("nhtsa.fuel_type_primary", "text"),
    "DriveType": ("nhtsa.drive_type", "text"),
}


@dataclass(frozen=True)
class NhtsaVpicEvidenceResult:
    evidence: RawEvidence
    facts: tuple[CandidateFact, ...]
    source_error_code: str | None
    source_error_text: str | None


def build_nhtsa_decode_vin_values_locator(vin: str, model_year: int) -> str:
    vin_text = vin.strip().upper() if isinstance(vin, str) else ""
    if not vin_text or len(vin_text) > 17:
        raise ValueError("VIN must be non-empty and at most 17 characters")
    if any(not (char.isdigit() or char in "ABCDEFGHJKLMNPRSTUVWXYZ*") for char in vin_text):
        raise ValueError("VIN contains unsupported characters")
    if not isinstance(model_year, int) or isinstance(model_year, bool) or model_year < 1981:
        raise ValueError("model_year must be an integer >= 1981")
    encoded_vin = quote(vin_text, safe="*")
    return (
        "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"
        f"{encoded_vin}?format=json&modelyear={model_year}"
    )


def _normalize_source_value(value: Any, kind: str, source_field: str) -> Any | None:
    if value is None:
        return None
    if kind == "text":
        if not isinstance(value, str):
            raise ValueError(f"NHTSA field {source_field!r} must be text")
        stripped = value.strip()
        return stripped or None
    if kind == "int":
        if isinstance(value, bool):
            raise ValueError(f"NHTSA field {source_field!r} must be an integer")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        raise ValueError(f"NHTSA field {source_field!r} must be an integer")
    raise AssertionError(f"unsupported field kind {kind!r}")


def _validate_raw_content_ref(raw_content_ref: str, digest: str) -> str:
    if not isinstance(raw_content_ref, str):
        raise ValueError("raw_content_ref is required")
    match = _RAW_REF_PATTERN.fullmatch(raw_content_ref)
    if match is None:
        raise ValueError("raw_content_ref must be a content-addressed sha256 reference")
    referenced_digest, retained_location = match.groups()
    if referenced_digest != digest:
        raise ValueError("raw_content_ref digest does not match raw_payload")
    if not retained_location.strip():
        raise ValueError("raw_content_ref must retain a snapshot location")
    return raw_content_ref


def _optional_source_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"NHTSA field {field!r} must be text when present")
    stripped = value.strip()
    return stripped or None


def _validate_decode_error_code(value: Any) -> str | None:
    error_code = _optional_source_text(value, "ErrorCode")
    if error_code is None:
        raise ValueError("NHTSA response requires ErrorCode")
    codes = tuple(code.strip() for code in error_code.split(","))
    if any(not code.isdigit() for code in codes):
        raise ValueError("NHTSA ErrorCode must contain comma-separated numeric codes")
    unsupported = sorted(set(codes) - _ALLOWED_DECODE_ERROR_CODES)
    if unsupported:
        raise ValueError(
            "NHTSA response contains unsupported decode error code(s): "
            + ", ".join(unsupported)
        )
    return error_code


def parse_nhtsa_decode_vin_values(
    raw_payload: bytes,
    *,
    locator: str,
    raw_content_ref: str,
    retrieved_at: datetime,
    entity_candidate_id: str,
) -> NhtsaVpicEvidenceResult:
    if not isinstance(raw_payload, bytes) or not raw_payload:
        raise ValueError("raw_payload must be non-empty bytes")
    if not isinstance(locator, str) or not locator.startswith("https://vpic.nhtsa.dot.gov/"):
        raise ValueError("locator must be an HTTPS vPIC locator")
    if not isinstance(retrieved_at, datetime) or retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
        raise ValueError("retrieved_at must be timezone-aware")
    if not isinstance(entity_candidate_id, str) or not entity_candidate_id.strip():
        raise ValueError("entity_candidate_id is required")

    digest = hashlib.sha256(raw_payload).hexdigest()
    durable_raw_ref = _validate_raw_content_ref(raw_content_ref, digest)
    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("NHTSA response must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("NHTSA response must be a JSON object")

    count = payload.get("Count")
    results = payload.get("Results")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or count != 1
        or not isinstance(results, list)
        or len(results) != 1
        or not isinstance(results[0], dict)
    ):
        raise ValueError("NHTSA DecodeVinValues response must contain exactly one result")
    row = results[0]
    source_error_code = _validate_decode_error_code(row.get("ErrorCode"))
    source_error_text = _optional_source_text(row.get("ErrorText"), "ErrorText")

    for required in ("Make", "Model", "ModelYear"):
        value = row.get(required)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"NHTSA response requires non-empty {required}")

    evidence_id = f"nhtsa-vpic:{digest}"
    evidence = RawEvidence(
        id=evidence_id,
        source_id=NHTSA_VPIC_SOURCE_ID,
        locator=locator,
        retrieved_at=retrieved_at,
        acquisition_method="direct_http_json",
        raw_content_ref=durable_raw_ref,
    )

    facts: list[CandidateFact] = []
    for source_field, (attribute, kind) in _FIELD_MAP.items():
        normalized = _normalize_source_value(row.get(source_field), kind, source_field)
        if normalized is None:
            continue
        facts.append(
            CandidateFact(
                id=f"{evidence_id}:{source_field}",
                entity_candidate_id=entity_candidate_id.strip(),
                attribute=attribute,
                raw_value=row[source_field],
                normalized_value=normalized,
                unit=None,
                evidence_id=evidence_id,
                extraction_method=NHTSA_VPIC_EXTRACTION_METHOD,
                confidence=None,
                normalization_rule="nhtsa_vpic:explicit-field:v1",
            )
        )

    return NhtsaVpicEvidenceResult(
        evidence=evidence,
        facts=tuple(facts),
        source_error_code=source_error_code,
        source_error_text=source_error_text,
    )


__all__ = [
    "NHTSA_VPIC_EXTRACTION_METHOD",
    "NHTSA_VPIC_SOURCE_ID",
    "NhtsaVpicEvidenceResult",
    "build_nhtsa_decode_vin_values_locator",
    "parse_nhtsa_decode_vin_values",
]
