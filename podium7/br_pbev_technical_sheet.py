from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable

from .inmetro_pbev_benchmark import (
    InmetroPbevQuantitativeBenchmark,
    InmetroPbevQuantitativeBenchmarkCase,
    PLACEHOLDER_TOKEN,
)


CONTRACT_SCHEMA = "podium7.br-pbev-technical-sheet.v1"

_COLUMN_FIELDS = {
    17: ("ethanol_city_consumption", "km/l", "number"),
    18: ("ethanol_road_consumption", "km/l", "number"),
    19: ("gasoline_city_consumption", "km/l", "number"),
    20: ("gasoline_road_consumption", "km/l", "number"),
    21: ("electric_equivalent_city_efficiency", "km/le", "number"),
    22: ("electric_equivalent_road_efficiency", "km/le", "number"),
    23: ("energy_consumption", "MJ/km", "number"),
    24: ("electric_range", "km", "number"),
    25: ("pbe_relative_class", None, "text"),
    26: ("pbe_general_class", None, "text"),
    27: ("conpet_symbol", None, "text"),
}

CONTRACT_FIELDS = frozenset(field for field, _, _ in _COLUMN_FIELDS.values())


@dataclass(frozen=True)
class PbevTechnicalSheetFact:
    field: str
    knowledge_state: str
    provenance_ref: str
    raw_value: str
    value: Any | None = None
    unit: str | None = None
    reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        field = _text(self.field, "field")
        if field not in CONTRACT_FIELDS:
            raise ValueError(f"unsupported PBEV technical-sheet field {field!r}")
        state = _text(self.knowledge_state, "knowledge_state")
        if state not in {"known", "not_applicable"}:
            raise ValueError("PBEV technical-sheet facts must be known or not_applicable")
        provenance_ref = _text(self.provenance_ref, "provenance_ref")
        raw_value = _text(self.raw_value, "raw_value")

        payload: dict[str, Any] = {
            "field": field,
            "knowledgeState": state,
            "provenanceRef": provenance_ref,
            "rawValue": raw_value,
        }
        if state == "known":
            if self.value is None:
                raise ValueError("known PBEV technical-sheet facts require value")
            payload["value"] = self.value
            if self.unit is not None:
                payload["unit"] = _text(self.unit, "unit")
        else:
            if self.value is not None or self.unit is not None:
                raise ValueError("not_applicable PBEV technical-sheet facts cannot carry value or unit")
            payload["reason"] = _text(self.reason, "reason")
        _ensure_strict_json(payload)
        return payload


def _text(value: str | None, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _ensure_strict_json(value: Any) -> None:
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("PBEV technical-sheet payload must be strict JSON-compatible") from exc


def _revision(vehicle_id: str, facts: list[dict[str, Any]]) -> str:
    material = {"schema": CONTRACT_SCHEMA, "vehicleId": vehicle_id, "facts": facts}
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def _vehicle_id(case: InmetroPbevQuantitativeBenchmarkCase) -> str:
    return "podium7:pbev:" + case.id.removeprefix("pbev-")


def _fact_from_column(case: InmetroPbevQuantitativeBenchmarkCase, column: int, expectation: Any) -> PbevTechnicalSheetFact:
    field, expected_unit, expected_kind = _COLUMN_FIELDS[column]
    provenance = f"inmetro:pbev:{case.id}:column:{column}"
    if expectation.state == "PLACEHOLDER":
        if expectation.raw != PLACEHOLDER_TOKEN:
            raise ValueError("PBEV placeholder facts must preserve the source placeholder token")
        return PbevTechnicalSheetFact(
            field=field,
            knowledge_state="not_applicable",
            provenance_ref=provenance,
            raw_value=expectation.raw,
            reason="source cell is the retained PBEV not-applicable placeholder",
        )

    if expectation.kind != expected_kind:
        raise ValueError(f"PBEV field {field!r} expected {expected_kind} source value")
    if expectation.unit != expected_unit:
        raise ValueError(f"PBEV field {field!r} expected unit {expected_unit!r}")
    return PbevTechnicalSheetFact(
        field=field,
        knowledge_state="known",
        provenance_ref=provenance,
        raw_value=expectation.raw,
        value=expectation.value,
        unit=expectation.unit,
    )


def publish_pbev_technical_sheet_payload(
    vehicle_id: str,
    facts: Iterable[PbevTechnicalSheetFact],
) -> dict[str, Any]:
    canonical_vehicle_id = _text(vehicle_id, "vehicle_id")
    fact_payloads = [fact.to_payload() for fact in facts]
    fact_payloads.sort(key=lambda item: item["field"])
    fields = [item["field"] for item in fact_payloads]
    if fields != sorted(CONTRACT_FIELDS):
        missing = sorted(CONTRACT_FIELDS - set(fields))
        extra = sorted(set(fields) - CONTRACT_FIELDS)
        raise ValueError(f"PBEV technical-sheet payload must cover every field; missing={missing}; extra={extra}")
    if len(fields) != len(set(fields)):
        raise ValueError("PBEV technical-sheet payload cannot contain duplicate fields")
    return {
        "schema": CONTRACT_SCHEMA,
        "vehicleId": canonical_vehicle_id,
        "revision": _revision(canonical_vehicle_id, fact_payloads),
        "facts": fact_payloads,
        "source": {
            "family": "INMETRO_PBEV",
            "market": "BR",
            "identityBoundary": "quantitative facts do not participate in identity resolution",
        },
    }


def publish_pbev_technical_sheets_from_benchmark(
    benchmark: InmetroPbevQuantitativeBenchmark,
) -> tuple[dict[str, Any], ...]:
    if benchmark.identity_boundary.get("quantitativeFactsParticipateInIdentityResolution") is not False:
        raise ValueError("PBEV technical-sheet publication requires identity-independent quantitative facts")
    sheets = []
    for case in benchmark.cases:
        facts = [_fact_from_column(case, column, expectation) for column, expectation in case.expected_columns]
        sheets.append(publish_pbev_technical_sheet_payload(_vehicle_id(case), facts))
    return tuple(sorted(sheets, key=lambda item: item["vehicleId"]))


__all__ = [
    "CONTRACT_FIELDS",
    "CONTRACT_SCHEMA",
    "PbevTechnicalSheetFact",
    "publish_pbev_technical_sheet_payload",
    "publish_pbev_technical_sheets_from_benchmark",
]
