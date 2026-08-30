from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


INMETRO_PBEV_QUANTITATIVE_SCHEMA = "podium7.inmetro-pbev-quantitative-semantics.v1"


@dataclass(frozen=True)
class InmetroPbevQuantitativeIdentity:
    category: str
    make: str
    model: str
    version: str
    engine: str
    propulsion: str
    fuel_code: str


@dataclass(frozen=True)
class InmetroPbevQuantitativeBenchmarkCase:
    id: str
    row_reference: str
    source_url: str
    source_excerpt: str
    identity: InmetroPbevQuantitativeIdentity
    quantitative: dict[str, Any]
    expected_missing: tuple[str, ...]


@dataclass(frozen=True)
class InmetroPbevQuantitativeBenchmark:
    version: str
    artifact: str
    cases: tuple[InmetroPbevQuantitativeBenchmarkCase, ...]


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _require_number(value: Any, field: str) -> float | int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric when provided")
    return value


def _validate_expected_missing(values: Any, *, case_id: str) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise ValueError(f"benchmark case {case_id!r} requires expectedMissing as a list")
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"benchmark case {case_id!r} has invalid expectedMissing entries")
    if len(set(values)) != len(values):
        raise ValueError(f"benchmark case {case_id!r} expectedMissing entries must be unique")
    return tuple(values)


def load_inmetro_pbev_quantitative_benchmark(path: str | Path) -> InmetroPbevQuantitativeBenchmark:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != INMETRO_PBEV_QUANTITATIVE_SCHEMA:
        raise ValueError("unsupported Inmetro PBEV quantitative benchmark schema")

    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Inmetro PBEV quantitative benchmark datasetVersion is required")

    artifact = payload.get("artifact")
    if artifact != "INMETRO_PBEV_QUANTITATIVE_SEMANTICS_V1":
        raise ValueError("Inmetro PBEV quantitative benchmark artifact is unsupported")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("Inmetro PBEV quantitative benchmark cases are required")

    cases: list[InmetroPbevQuantitativeBenchmarkCase] = []
    seen_ids: set[str] = set()
    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise ValueError("Inmetro PBEV quantitative benchmark case must be an object")

        case_id = raw.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Inmetro PBEV quantitative benchmark case id is required")
        if case_id in seen_ids:
            raise ValueError(f"duplicate Inmetro PBEV benchmark case id {case_id!r}")
        seen_ids.add(case_id)

        row_reference = raw.get("rowReference")
        if not isinstance(row_reference, str) or not row_reference.strip():
            raise ValueError(f"benchmark case {case_id!r} requires rowReference")

        source_url = raw.get("sourceUrl")
        if not isinstance(source_url, str) or not source_url.startswith("https://www.gov.br/inmetro/"):
            raise ValueError(f"benchmark case {case_id!r} requires an official Inmetro https sourceUrl")

        source_excerpt = raw.get("sourceExcerpt")
        if not isinstance(source_excerpt, str) or not source_excerpt.strip():
            raise ValueError(f"benchmark case {case_id!r} requires sourceExcerpt")

        identity_raw = raw.get("identity")
        if not isinstance(identity_raw, dict):
            raise ValueError(f"benchmark case {case_id!r} requires identity")
        identity = InmetroPbevQuantitativeIdentity(
            category=identity_raw["category"],
            make=identity_raw["make"],
            model=identity_raw["model"],
            version=identity_raw["version"],
            engine=identity_raw["engine"],
            propulsion=identity_raw["propulsion"],
            fuel_code=identity_raw["fuelCode"],
        )
        if any(not getattr(identity, field).strip() for field in identity.__dataclass_fields__):
            raise ValueError(f"benchmark case {case_id!r} identity fields must be non-empty")

        quantitative = raw.get("quantitative")
        if not isinstance(quantitative, dict):
            raise ValueError(f"benchmark case {case_id!r} requires quantitative")
        emissions = quantitative.get("emissions")
        consumption = quantitative.get("consumption")
        comparison = quantitative.get("comparison")
        if not isinstance(emissions, dict) or not isinstance(consumption, dict) or not isinstance(comparison, dict):
            raise ValueError(f"benchmark case {case_id!r} requires emissions, consumption and comparison blocks")

        if not isinstance(quantitative.get("transmissionCode"), str) or not quantitative["transmissionCode"].strip():
            raise ValueError(f"benchmark case {case_id!r} requires transmissionCode")
        if not isinstance(quantitative.get("steeringAssistCode"), str) or not quantitative["steeringAssistCode"].strip():
            raise ValueError(f"benchmark case {case_id!r} requires steeringAssistCode")
        if not isinstance(quantitative.get("vehpCode"), str) or not quantitative["vehpCode"].strip():
            raise ValueError(f"benchmark case {case_id!r} requires vehpCode")

        propulsion = identity.propulsion.casefold()
        fuel_code = identity.fuel_code.casefold()
        if propulsion == "elétrico":
            if fuel_code != "e":
                raise ValueError(f"benchmark case {case_id!r} electric cases require fuelCode E")
            if emissions.get("tailpipeCo2Gkm") is not None or emissions.get("tailpipeCo2eGkm") is not None:
                raise ValueError(f"benchmark case {case_id!r} electric emissions must be absent")
            if consumption.get("cityKmL") is not None or consumption.get("roadKmL") is not None:
                raise ValueError(f"benchmark case {case_id!r} electric combustion consumption must be absent")
            if not isinstance(consumption.get("cityKmLe"), (int, float)) or isinstance(consumption.get("cityKmLe"), bool):
                raise ValueError(f"benchmark case {case_id!r} electric cityKmLe must be numeric")
            if not isinstance(consumption.get("roadKmLe"), (int, float)) or isinstance(consumption.get("roadKmLe"), bool):
                raise ValueError(f"benchmark case {case_id!r} electric roadKmLe must be numeric")
        else:
            if fuel_code != "f":
                raise ValueError(f"benchmark case {case_id!r} non-electric cases in this benchmark require fuelCode F")
            _require_number(emissions.get("tailpipeCo2Gkm"), f"benchmark case {case_id!r} emissions.tailpipeCo2Gkm")
            _require_number(emissions.get("tailpipeCo2eGkm"), f"benchmark case {case_id!r} emissions.tailpipeCo2eGkm")
            _require_number(consumption.get("cityKmL"), f"benchmark case {case_id!r} consumption.cityKmL")
            _require_number(consumption.get("roadKmL"), f"benchmark case {case_id!r} consumption.roadKmL")
            _require_number(consumption.get("cityKmLe"), f"benchmark case {case_id!r} consumption.cityKmLe")
            _require_number(consumption.get("roadKmLe"), f"benchmark case {case_id!r} consumption.roadKmLe")

        _require_number(comparison.get("relative"), f"benchmark case {case_id!r} comparison.relative")
        for field in ("absoluteGrade", "generalGrade"):
            value = comparison.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"benchmark case {case_id!r} comparison.{field} is required")

        expected_missing = _validate_expected_missing(raw.get("expectedMissing"), case_id=case_id)

        cases.append(
            InmetroPbevQuantitativeBenchmarkCase(
                id=case_id,
                row_reference=row_reference,
                source_url=source_url,
                source_excerpt=source_excerpt,
                identity=identity,
                quantitative={
                    "transmissionCode": quantitative["transmissionCode"],
                    "steeringAssistCode": quantitative["steeringAssistCode"],
                    "vehpCode": quantitative["vehpCode"],
                    "emissions": dict(emissions),
                    "consumption": dict(consumption),
                    "comparison": dict(comparison),
                },
                expected_missing=expected_missing,
            )
        )

    return InmetroPbevQuantitativeBenchmark(
        version=version,
        artifact=artifact,
        cases=tuple(cases),
    )


def evaluate_inmetro_pbev_quantitative_benchmark(
    benchmark: InmetroPbevQuantitativeBenchmark,
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    kind_counts = {"electric": 0, "combustion": 0, "hybrid": 0}
    numeric_count = 0
    missing_count = 0
    grade_count = 0

    for case in benchmark.cases:
        propulsion = case.identity.propulsion.casefold()
        if propulsion == "elétrico":
            kind = "electric"
        elif propulsion == "híbrido":
            kind = "hybrid"
        else:
            kind = "combustion"
        kind_counts[kind] += 1

        emissions = case.quantitative["emissions"]
        consumption = case.quantitative["consumption"]
        comparison = case.quantitative["comparison"]

        quantitative_fields = (
            emissions.get("tailpipeCo2Gkm"),
            emissions.get("tailpipeCo2eGkm"),
            consumption.get("cityKmL"),
            consumption.get("roadKmL"),
            consumption.get("cityKmLe"),
            consumption.get("roadKmLe"),
            comparison.get("relative"),
        )
        numeric_present = sum(value is not None for value in quantitative_fields)
        numeric_missing = sum(value is None for value in quantitative_fields)
        grade_present = sum(bool(comparison.get(field)) for field in ("absoluteGrade", "generalGrade"))

        numeric_count += numeric_present
        missing_count += numeric_missing
        grade_count += grade_present

        cases.append(
            {
                "id": case.id,
                "kind": kind,
                "numericPresent": numeric_present,
                "numericMissing": numeric_missing,
                "gradePresent": grade_present,
                "expectedMissing": list(case.expected_missing),
                "sourceReference": case.row_reference,
            }
        )

    total_cases = len(benchmark.cases)
    complete_cases = sum(case["numericMissing"] == len(case["expectedMissing"]) for case in cases)
    return {
        "schema": "podium7.inmetro-pbev-quantitative-report.v1",
        "datasetVersion": benchmark.version,
        "artifact": benchmark.artifact,
        "totalCases": total_cases,
        "metrics": {
            "electricCaseCount": kind_counts["electric"],
            "combustionCaseCount": kind_counts["combustion"],
            "hybridCaseCount": kind_counts["hybrid"],
            "numericMeasurementCount": numeric_count,
            "numericMissingCount": missing_count,
            "gradeObservationCount": grade_count,
            "completeCaseCount": complete_cases,
            "numericCoverage": _rate(numeric_count, numeric_count + missing_count),
        },
        "cases": cases,
    }


__all__ = [
    "INMETRO_PBEV_QUANTITATIVE_SCHEMA",
    "InmetroPbevQuantitativeBenchmark",
    "InmetroPbevQuantitativeBenchmarkCase",
    "InmetroPbevQuantitativeIdentity",
    "evaluate_inmetro_pbev_quantitative_benchmark",
    "load_inmetro_pbev_quantitative_benchmark",
]
