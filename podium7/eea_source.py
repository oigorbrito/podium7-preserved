from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from .normalization import normalize_fact


@dataclass(frozen=True)
class EeaIdentityEvidence:
    source_record_id: int
    member_state: str
    make: str
    commercial_name: str
    manufacturer: str
    type_approval_number: str | None
    vehicle_type: str | None
    variant: str | None
    version: str | None
    registration_year: int
    status: str | None


@dataclass(frozen=True)
class EeaRegulatoryEvidence:
    mass_in_running_order_kg: int | None
    engine_capacity_cm3: int | None
    engine_power_kw: int | None
    fuel_type: str | None
    fuel_mode: str | None
    wltp_co2_g_km: int | None
    electric_energy_consumption_wh_km: int | None


@dataclass(frozen=True)
class EeaExtractedFact:
    attribute: str
    raw_value: object
    normalized_value: object
    unit: str | None
    source_field: str
    extraction_rule: str
    normalization_rule: str


@dataclass(frozen=True)
class EeaExtractionIssue:
    attribute: str
    source_field: str
    code: str
    message: str
    raw_value: object | None = None


@dataclass(frozen=True)
class EeaRecordReport:
    identity: EeaIdentityEvidence
    regulatory: EeaRegulatoryEvidence
    facts: tuple[EeaExtractedFact, ...]
    issues: tuple[EeaExtractionIssue, ...]


# V1 deliberately supports only source combinations covered by the frozen
# benchmark and primary EEA fuel-mode semantics. Adding another combination is
# a source-family change, not a generic token-normalization fallback.
_FUEL_SEMANTICS: dict[tuple[str, str], str] = {
    ("electric", "e"): "electric",
    ("petrol", "m"): "gasoline",
    ("petrol", "h"): "hybrid",
    ("petrol/electric", "p"): "plug-in hybrid",
}


def _reject_non_standard_json(value: str) -> None:
    raise ValueError(f"non-standard JSON constant is not allowed: {value}")


def load_eea_response(payload: bytes | str) -> tuple[dict[str, Any], ...]:
    if isinstance(payload, bytes):
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("EEA response must be UTF-8 JSON") from exc
    elif isinstance(payload, str):
        text = payload
    else:
        raise TypeError("EEA response must be bytes or text")

    try:
        root = json.loads(text, parse_constant=_reject_non_standard_json)
    except json.JSONDecodeError as exc:
        raise ValueError("EEA response is not valid JSON") from exc

    if not isinstance(root, dict):
        raise ValueError("EEA response root must be an object")
    if "error" in root:
        raise ValueError(f"EEA response contains API error: {root['error']!r}")

    results = root.get("results")
    if not isinstance(results, list):
        raise ValueError("EEA response requires a results array")

    rows: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    for index, row in enumerate(results):
        if not isinstance(row, dict):
            raise ValueError(f"EEA results[{index}] must be an object")
        record_id = row.get("ID")
        if isinstance(record_id, bool) or not isinstance(record_id, int):
            raise ValueError(f"EEA results[{index}] requires integer ID")
        if record_id in seen_ids:
            raise ValueError(f"duplicate EEA source record ID {record_id}")
        seen_ids.add(record_id)
        rows.append(row)

    return tuple(rows)


def _required_text(row: dict[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"EEA field {field!r} must be non-empty text")
    return value.strip()


def _optional_text(row: dict[str, Any], field: str) -> str | None:
    value = row.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"EEA field {field!r} must be text or null")
    stripped = value.strip()
    return stripped or None


def _required_int(row: dict[str, Any], field: str) -> int:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"EEA field {field!r} must be an integer")
    return value


def _optional_int(row: dict[str, Any], field: str) -> int | None:
    value = row.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"EEA field {field!r} must be an integer or null")
    return value


def _identity(row: dict[str, Any]) -> EeaIdentityEvidence:
    return EeaIdentityEvidence(
        source_record_id=_required_int(row, "ID"),
        member_state=_required_text(row, "MS"),
        make=_required_text(row, "Mk"),
        commercial_name=_required_text(row, "Cn"),
        manufacturer=_required_text(row, "Man"),
        type_approval_number=_optional_text(row, "TAN"),
        vehicle_type=_optional_text(row, "T"),
        variant=_optional_text(row, "Va"),
        version=_optional_text(row, "Ve"),
        registration_year=_required_int(row, "Year"),
        status=_optional_text(row, "Status"),
    )


def _regulatory(row: dict[str, Any]) -> EeaRegulatoryEvidence:
    return EeaRegulatoryEvidence(
        mass_in_running_order_kg=_optional_int(row, "M (kg)"),
        engine_capacity_cm3=_optional_int(row, "Ec (cm3)"),
        engine_power_kw=_optional_int(row, "Ep (KW)"),
        fuel_type=_optional_text(row, "Ft"),
        fuel_mode=_optional_text(row, "Fm"),
        wltp_co2_g_km=_optional_int(row, "Ewltp (g/km)"),
        electric_energy_consumption_wh_km=_optional_int(row, "Z (Wh/km)"),
    )


def _normalized_fact(
    attribute: str,
    raw_value: object,
    source_field: str,
    source_unit: str | None,
    extraction_rule: str,
) -> tuple[EeaExtractedFact | None, EeaExtractionIssue | None]:
    try:
        normalized = normalize_fact(attribute, raw_value, source_unit)
    except ValueError as exc:
        return None, EeaExtractionIssue(
            attribute=attribute,
            source_field=source_field,
            code="INVALID_VALUE",
            message=f"EEA field {source_field!r} rejected for {attribute!r}: {exc}",
            raw_value=raw_value,
        )
    return (
        EeaExtractedFact(
            attribute=attribute,
            raw_value=raw_value,
            normalized_value=normalized.value,
            unit=normalized.unit,
            source_field=source_field,
            extraction_rule=extraction_rule,
            normalization_rule=normalized.rule,
        ),
        None,
    )


def _append_numeric_fact(
    row: dict[str, Any],
    facts: list[EeaExtractedFact],
    issues: list[EeaExtractionIssue],
    *,
    source_field: str,
    attribute: str,
    unit: str,
    required: bool,
) -> None:
    raw_value = row.get(source_field)
    if raw_value is None or raw_value == "":
        if required:
            issues.append(
                EeaExtractionIssue(
                    attribute=attribute,
                    source_field=source_field,
                    code="MISSING_FACT",
                    message=f"EEA field {source_field!r} is missing for {attribute!r}",
                )
            )
        return

    fact, issue = _normalized_fact(
        attribute,
        raw_value,
        source_field,
        unit,
        f"eea.{attribute}.structured.v1",
    )
    if issue is not None:
        issues.append(issue)
    elif fact is not None:
        facts.append(fact)


def _append_fuel_fact(
    row: dict[str, Any],
    facts: list[EeaExtractedFact],
    issues: list[EeaExtractionIssue],
) -> None:
    fuel_type = row.get("Ft")
    fuel_mode = row.get("Fm")
    if not isinstance(fuel_type, str) or not fuel_type.strip():
        issues.append(
            EeaExtractionIssue(
                attribute="fuel_type",
                source_field="Ft/Fm",
                code="MISSING_FACT",
                message="EEA fuel type is missing",
            )
        )
        return
    if not isinstance(fuel_mode, str) or not fuel_mode.strip():
        issues.append(
            EeaExtractionIssue(
                attribute="fuel_type",
                source_field="Ft/Fm",
                code="MISSING_FUEL_MODE",
                message="EEA fuel mode is required for conservative fuel semantics",
                raw_value=fuel_type,
            )
        )
        return

    key = (fuel_type.strip().casefold(), fuel_mode.strip().casefold())
    semantic_value = _FUEL_SEMANTICS.get(key)
    if semantic_value is None:
        issues.append(
            EeaExtractionIssue(
                attribute="fuel_type",
                source_field="Ft/Fm",
                code="UNSUPPORTED_FUEL_SEMANTICS",
                message=f"unsupported EEA fuel type/mode combination {key!r}",
                raw_value={"Ft": fuel_type, "Fm": fuel_mode},
            )
        )
        return

    fact, issue = _normalized_fact(
        "fuel_type",
        semantic_value,
        "Ft/Fm",
        None,
        "eea.fuel_type_mode.structured.v1",
    )
    if issue is not None:
        issues.append(issue)
    elif fact is not None:
        facts.append(fact)


def extract_eea_record_report(row: dict[str, Any]) -> EeaRecordReport:
    if not isinstance(row, dict):
        raise TypeError("EEA row must be an object")

    identity = _identity(row)
    regulatory = _regulatory(row)
    facts: list[EeaExtractedFact] = []
    issues: list[EeaExtractionIssue] = []

    _append_fuel_fact(row, facts, issues)
    _append_numeric_fact(
        row,
        facts,
        issues,
        source_field="Ep (KW)",
        attribute="power",
        unit="kW",
        required=True,
    )
    _append_numeric_fact(
        row,
        facts,
        issues,
        source_field="Ec (cm3)",
        attribute="displacement",
        unit="cc",
        required=(regulatory.fuel_type or "").casefold() != "electric",
    )

    # M (kg) is retained above as EEA's regulatory "mass in running order".
    # It is deliberately not promoted to Podium curb_weight because unit
    # compatibility alone does not establish semantic equivalence.
    return EeaRecordReport(identity, regulatory, tuple(facts), tuple(issues))


def extract_eea_record(row: dict[str, Any]) -> EeaRecordReport:
    report = extract_eea_record_report(row)
    if report.issues:
        raise ValueError(report.issues[0].message)
    return report


def extract_eea_response(payload: bytes | str) -> tuple[EeaRecordReport, ...]:
    return tuple(extract_eea_record_report(row) for row in load_eea_response(payload))
