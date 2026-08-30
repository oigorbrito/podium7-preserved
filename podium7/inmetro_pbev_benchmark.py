from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import pdfplumber


INMETRO_PBEV_QUANTITATIVE_SCHEMA = "podium7.pbev-quantitative-semantics.v1"
EXPECTED_TABLE_WIDTH = 28
PLACEHOLDER_TOKEN = "\\"

@dataclass(frozen=True)
class InmetroPbevSource:
    publisher: str
    landing_page: str
    document_locator: str
    document_page: int
    raw_content_sha256: str
    snapshot_retrievability: str
    snapshot_locator: str


@dataclass(frozen=True)
class InmetroPbevCellExpectation:
    state: str
    raw: str
    kind: str | None = None
    value: Any | None = None
    unit: str | None = None


@dataclass(frozen=True)
class InmetroPbevQuantitativeIdentity:
    category: str
    make: str
    model: str
    version: str
    engine: str
    propulsion: str
    transmission: str
    air_conditioning: str
    steering_assist: str
    fuel: str


@dataclass(frozen=True)
class InmetroPbevQuantitativeBenchmarkCase:
    id: str
    evidence_locator: str
    identity: InmetroPbevQuantitativeIdentity
    expected_columns: tuple[tuple[int, InmetroPbevCellExpectation], ...]


@dataclass(frozen=True)
class InmetroPbevQuantitativeBenchmark:
    version: str
    status: str
    source: InmetroPbevSource
    table_width: int
    blocked_columns: tuple[dict[str, Any], ...]
    identity_boundary: dict[str, Any]
    cases: tuple[InmetroPbevQuantitativeBenchmarkCase, ...]


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _normalize_text(value: str | None) -> str:
    return " ".join((value or "").split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value


def _parse_cell_expectation(column: str, payload: Any) -> tuple[int, InmetroPbevCellExpectation]:
    if not isinstance(payload, dict):
        raise ValueError(f"column {column} must be an object")
    if "state" not in payload or "raw" not in payload:
        raise ValueError(f"column {column} requires state and raw")
    state = _require_str(payload["state"], f"column {column} state").upper()
    raw = _require_str(payload["raw"], f"column {column} raw")
    kind = payload.get("kind")
    if kind is not None:
        kind = _require_str(kind, f"column {column} kind").lower()
    value = payload.get("value")
    unit = payload.get("unit")
    if unit is not None:
        unit = _require_str(unit, f"column {column} unit")
    if state == "PLACEHOLDER":
        if raw != PLACEHOLDER_TOKEN:
            raise ValueError(f"column {column} placeholder raw must be a backslash")
        if value is not None or unit is not None or kind is not None:
            raise ValueError(f"column {column} placeholder must not define value/unit/kind")
    elif state == "VALUE":
        if kind not in {"number", "text"}:
            raise ValueError(f"column {column} value must declare kind number or text")
        if kind == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"column {column} numeric value must be numeric")
        elif not isinstance(value, str) or not value.strip():
            raise ValueError(f"column {column} text value must be non-empty text")
    else:
        raise ValueError(f"column {column} has unsupported state {state!r}")
    return int(column), InmetroPbevCellExpectation(state=state, raw=raw, kind=kind, value=value, unit=unit)


def _parse_identity(payload: dict[str, Any], *, case_id: str) -> InmetroPbevQuantitativeIdentity:
    return InmetroPbevQuantitativeIdentity(
        category=_require_str(payload.get("category"), f"case {case_id!r} identity.category"),
        make=_require_str(payload.get("make"), f"case {case_id!r} identity.make"),
        model=_require_str(payload.get("model"), f"case {case_id!r} identity.model"),
        version=_require_str(payload.get("version"), f"case {case_id!r} identity.version"),
        engine=_require_str(payload.get("engine"), f"case {case_id!r} identity.engine"),
        propulsion=_require_str(payload.get("propulsion"), f"case {case_id!r} identity.propulsion"),
        transmission=_require_str(payload.get("transmission"), f"case {case_id!r} identity.transmission"),
        air_conditioning=_require_str(payload.get("airConditioning"), f"case {case_id!r} identity.airConditioning"),
        steering_assist=_require_str(payload.get("steeringAssist"), f"case {case_id!r} identity.steeringAssist"),
        fuel=_require_str(payload.get("fuel"), f"case {case_id!r} identity.fuel"),
    )


def load_inmetro_pbev_quantitative_benchmark(path: str | Path) -> InmetroPbevQuantitativeBenchmark:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != INMETRO_PBEV_QUANTITATIVE_SCHEMA:
        raise ValueError("unsupported Inmetro PBEV quantitative benchmark schema")

    version = _require_str(payload.get("datasetVersion"), "Inmetro PBEV quantitative benchmark datasetVersion")
    status = _require_str(payload.get("status"), "Inmetro PBEV quantitative benchmark status")

    raw_source = payload.get("source")
    if not isinstance(raw_source, dict):
        raise ValueError("Inmetro PBEV quantitative benchmark source is required")
    source = InmetroPbevSource(
        publisher=_require_str(raw_source.get("publisher"), "benchmark source.publisher"),
        landing_page=_require_str(raw_source.get("landingPage"), "benchmark source.landingPage"),
        document_locator=_require_str(raw_source.get("documentLocator"), "benchmark source.documentLocator"),
        document_page=int(raw_source.get("documentPage")),
        raw_content_sha256=_require_str(raw_source.get("rawContentSha256"), "benchmark source.rawContentSha256"),
        snapshot_retrievability=_require_str(
            raw_source.get("snapshotRetrievability"), "benchmark source.snapshotRetrievability"
        ),
        snapshot_locator=_require_str(raw_source.get("snapshotLocator"), "benchmark source.snapshotLocator"),
    )
    if len(source.raw_content_sha256) != 64:
        raise ValueError("benchmark source.rawContentSha256 must be a SHA-256 hex digest")

    column_layout = payload.get("columnLayout")
    if not isinstance(column_layout, dict):
        raise ValueError("Inmetro PBEV quantitative benchmark columnLayout is required")
    table_width = column_layout.get("tableWidth")
    if table_width != EXPECTED_TABLE_WIDTH:
        raise ValueError("Inmetro PBEV quantitative benchmark requires a 28-column table")
    blocked_columns = column_layout.get("blockedColumns")
    if not isinstance(blocked_columns, list) or not blocked_columns:
        raise ValueError("Inmetro PBEV quantitative benchmark blockedColumns are required")
    for blocked in blocked_columns:
        if not isinstance(blocked, dict):
            raise ValueError("blockedColumns entries must be objects")
        _require_str(blocked.get("range"), "blockedColumns.range")
        _require_str(blocked.get("status"), "blockedColumns.status")
        _require_str(blocked.get("reason"), "blockedColumns.reason")

    identity_boundary = payload.get("identityBoundary")
    if not isinstance(identity_boundary, dict):
        raise ValueError("Inmetro PBEV quantitative benchmark identityBoundary is required")
    if identity_boundary.get("quantitativeFactsParticipateInIdentityResolution") is not False:
        raise ValueError("Inmetro PBEV quantitative benchmark must fail closed on identity boundary")
    _require_str(identity_boundary.get("rule"), "identityBoundary.rule")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("Inmetro PBEV quantitative benchmark cases are required")

    cases: list[InmetroPbevQuantitativeBenchmarkCase] = []
    seen_ids: set[str] = set()
    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise ValueError("Inmetro PBEV quantitative benchmark case must be an object")
        case_id = _require_str(raw.get("id"), "benchmark case id")
        if case_id in seen_ids:
            raise ValueError(f"duplicate benchmark case id {case_id!r}")
        seen_ids.add(case_id)
        evidence_locator = _require_str(raw.get("evidenceLocator"), f"benchmark case {case_id!r} evidenceLocator")

        identity_raw = raw.get("identity")
        if not isinstance(identity_raw, dict):
            raise ValueError(f"benchmark case {case_id!r} identity is required")
        identity = _parse_identity(identity_raw, case_id=case_id)

        expected_columns_raw = raw.get("expectedColumns")
        if not isinstance(expected_columns_raw, dict) or not expected_columns_raw:
            raise ValueError(f"benchmark case {case_id!r} expectedColumns is required")
        parsed_columns = tuple(
            sorted(
                _parse_cell_expectation(column, expectation)
                for column, expectation in expected_columns_raw.items()
            )
        )
        expected_index_set = {column for column, _ in parsed_columns}
        if expected_index_set != set(range(17, 28)):
            raise ValueError(f"benchmark case {case_id!r} must define columns 17-27 exactly")

        cases.append(
            InmetroPbevQuantitativeBenchmarkCase(
                id=case_id,
                evidence_locator=evidence_locator,
                identity=identity,
                expected_columns=parsed_columns,
            )
        )

    return InmetroPbevQuantitativeBenchmark(
        version=version,
        status=status,
        source=source,
        table_width=table_width,
        blocked_columns=tuple(blocked_columns),
        identity_boundary=dict(identity_boundary),
        cases=tuple(cases),
    )


def _extract_page_one_tables(pdf_path: Path) -> tuple[list[list[str | None]], ...]:
    with pdfplumber.open(pdf_path) as document:
        page = document.pages[0]
        tables = page.extract_tables(
            table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
        )
    if not tables:
        raise ValueError("Inmetro PBEV fixture page 1 yielded no tables")

    normalized: list[list[list[str | None]]] = []
    seen_header = False
    for table in tables:
        width = max(len(row) for row in table)
        if width != EXPECTED_TABLE_WIDTH:
            continue
        if any(len(row) != EXPECTED_TABLE_WIDTH for row in table):
            raise ValueError("Inmetro PBEV fixture page 1 layout changed; expected 28 columns")
        if table and _normalize_text(table[0][0]) == "Categoria" and _normalize_text(table[0][1]) == "Marca" and _normalize_text(table[0][2]) == "Modelo" and _normalize_text(table[0][3]) == "Versão" and _normalize_text(table[0][4]) == "Motor" and "Tipo de Propulsão" in _normalize_text(table[0][5]):
            seen_header = True
        normalized.append(table)
    if not normalized:
        raise ValueError("Inmetro PBEV fixture page 1 does not contain the expected 28-column table")
    if not seen_header:
        raise ValueError("Inmetro PBEV fixture page 1 header row no longer matches the retained layout")
    return tuple(normalized)


def extract_inmetro_pbev_quantitative_rows(pdf_path: str | Path) -> tuple[tuple[str, ...], ...]:
    path = Path(pdf_path)
    tables = _extract_page_one_tables(path)
    rows: list[tuple[str, ...]] = []
    for table in tables:
        for row in table:
            rows.append(tuple(_normalize_text(cell) for cell in row))
    return tuple(rows)


def _match_case_row(rows: tuple[tuple[str, ...], ...], identity: InmetroPbevQuantitativeIdentity) -> tuple[str, ...]:
    matches = [
        row
        for row in rows
        if len(row) == EXPECTED_TABLE_WIDTH
        and row[:10]
        == (
            identity.category,
            identity.make,
            identity.model,
            identity.version,
            identity.engine,
            identity.propulsion,
            identity.transmission,
            identity.air_conditioning,
            identity.steering_assist,
            identity.fuel,
        )
    ]
    if len(matches) != 1:
        raise ValueError(
            "Inmetro PBEV quantitative benchmark requires exactly one row per identity; "
            f"found {len(matches)}"
        )
    return matches[0]


def _compare_cell(expected: InmetroPbevCellExpectation, actual: str) -> dict[str, Any]:
    if expected.state == "PLACEHOLDER":
        if actual != PLACEHOLDER_TOKEN:
            raise ValueError("expected placeholder cell but found non-placeholder content")
        return {"state": expected.state, "raw": actual}

    if actual != expected.raw:
        raise ValueError(f"expected raw cell {expected.raw!r} but found {actual!r}")

    if expected.kind == "number":
        parsed = float(actual)
        expected_value = float(expected.value)
        if parsed != expected_value:
            raise ValueError(f"expected numeric value {expected_value!r} but found {parsed!r}")
        return {"state": expected.state, "raw": actual, "value": parsed, "unit": expected.unit}

    if expected.kind == "text":
        if actual != expected.value:
            raise ValueError(f"expected text value {expected.value!r} but found {actual!r}")
        return {"state": expected.state, "raw": actual, "value": actual, "unit": expected.unit}

    raise ValueError(f"unsupported expectation kind {expected.kind!r}")


def evaluate_inmetro_pbev_quantitative_benchmark(
    benchmark: InmetroPbevQuantitativeBenchmark,
    pdf_path: str | Path | None = None,
) -> dict[str, Any]:
    fixture = Path(pdf_path or benchmark.source.snapshot_locator)
    if not fixture.is_file():
        raise ValueError("Inmetro PBEV quantitative benchmark fixture is missing")
    if _sha256(fixture) != benchmark.source.raw_content_sha256:
        raise ValueError("Inmetro PBEV quantitative benchmark fixture hash mismatch")

    rows = extract_inmetro_pbev_quantitative_rows(fixture)
    results: list[dict[str, Any]] = []
    matched_cases = 0
    placeholder_cells = 0
    value_cells = 0
    zero_cells = 0

    for case in benchmark.cases:
        row = _match_case_row(rows, case.identity)
        observed_columns: dict[str, Any] = {}
        for column, expectation in case.expected_columns:
            actual = row[column]
            if expectation.state == "PLACEHOLDER":
                placeholder_cells += 1
            else:
                value_cells += 1
                if actual == "0":
                    zero_cells += 1
            observed_columns[str(column)] = _compare_cell(expectation, actual)
        matched_cases += 1
        results.append(
            {
                "id": case.id,
                "evidenceLocator": case.evidence_locator,
                "identity": {
                    "category": case.identity.category,
                    "make": case.identity.make,
                    "model": case.identity.model,
                    "version": case.identity.version,
                    "engine": case.identity.engine,
                    "propulsion": case.identity.propulsion,
                    "transmission": case.identity.transmission,
                    "airConditioning": case.identity.air_conditioning,
                    "steeringAssist": case.identity.steering_assist,
                    "fuel": case.identity.fuel,
                },
                "observedColumns": observed_columns,
            }
        )

    return {
        "schema": "podium7.inmetro-pbev-quantitative-report.v1",
        "datasetVersion": benchmark.version,
        "status": benchmark.status,
        "source": {
            "documentPage": benchmark.source.document_page,
            "rawContentSha256": benchmark.source.raw_content_sha256,
            "snapshotLocator": str(fixture),
        },
        "layout": {
            "tableWidth": benchmark.table_width,
            "blockedColumns": list(benchmark.blocked_columns),
        },
        "metrics": {
            "caseCount": len(benchmark.cases),
            "matchedCaseCount": matched_cases,
            "placeholderCellCount": placeholder_cells,
            "valueCellCount": value_cells,
            "zeroCellCount": zero_cells,
            "placeholderCoverage": _rate(placeholder_cells, placeholder_cells + value_cells),
        },
        "cases": results,
    }


__all__ = [
    "EXPECTED_TABLE_WIDTH",
    "INMETRO_PBEV_QUANTITATIVE_SCHEMA",
    "InmetroPbevCellExpectation",
    "InmetroPbevQuantitativeBenchmark",
    "InmetroPbevQuantitativeBenchmarkCase",
    "InmetroPbevQuantitativeIdentity",
    "InmetroPbevSource",
    "evaluate_inmetro_pbev_quantitative_benchmark",
    "extract_inmetro_pbev_quantitative_rows",
    "load_inmetro_pbev_quantitative_benchmark",
]
