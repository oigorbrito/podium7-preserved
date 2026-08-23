from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any

from .web_extraction import (
    AUTOEVOLUTION_ARTEGA_GT_RULES_V1,
    AUTOEVOLUTION_ARTEGA_GT_RULES_V2,
    WebFieldRule,
    extract_with_rules,
    extract_with_rules_report,
)


WEB_EXTRACTION_CORPUS_SCHEMA = "podium7.web-extraction-source-family-corpus.v1"
WEB_EXTRACTION_BOUNDED_GOLD_SCHEMA = "podium7.web-extraction-bounded-gold.v1"


@dataclass(frozen=True)
class WebExtractionCorpusCase:
    id: str
    manufacturer: str
    source_url: str
    snapshot_path: Path
    source_target_field_count: int
    expected_outcome: str
    expected_parsed: dict[str, object]
    expected_failure_contains: str | None
    non_scalar_target_fields: tuple[str, ...]
    label_variants: dict[str, str]


@dataclass(frozen=True)
class WebExtractionCorpus:
    version: str
    artifact: str
    cases: tuple[WebExtractionCorpusCase, ...]


@dataclass(frozen=True)
class WebExtractionBoundedGold:
    version: str
    base_dataset_version: str
    artifact: str
    expected_by_case: dict[str, dict[str, object]]


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def load_web_extraction_corpus(path: str | Path) -> WebExtractionCorpus:
    dataset_path = Path(path).resolve()
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if payload.get("schema") != WEB_EXTRACTION_CORPUS_SCHEMA:
        raise ValueError("unsupported web extraction corpus schema")

    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("web extraction corpus datasetVersion is required")

    artifact = payload.get("artifact")
    if artifact != "AUTOEVOLUTION_ARTEGA_GT_RULES":
        raise ValueError("web extraction corpus artifact is unsupported")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("web extraction corpus cases are required")

    repo_root = dataset_path.parent.parent
    cases: list[WebExtractionCorpusCase] = []
    seen_ids: set[str] = set()
    for raw in raw_cases:
        case_id = raw.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("web extraction corpus case id is required")
        if case_id in seen_ids:
            raise ValueError(f"duplicate web extraction corpus case id {case_id!r}")
        seen_ids.add(case_id)

        manufacturer = raw.get("manufacturer")
        if not isinstance(manufacturer, str) or not manufacturer.strip():
            raise ValueError(f"case {case_id!r} requires manufacturer")

        source_url = raw.get("sourceUrl")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            raise ValueError(f"case {case_id!r} requires an https sourceUrl")

        snapshot = raw.get("snapshot")
        if not isinstance(snapshot, str) or not snapshot.strip():
            raise ValueError(f"case {case_id!r} requires snapshot")
        snapshot_path = (repo_root / snapshot).resolve()
        try:
            snapshot_path.relative_to(repo_root)
        except ValueError as exc:
            raise ValueError(f"case {case_id!r} snapshot escapes repository root") from exc
        if not snapshot_path.is_file():
            raise ValueError(f"case {case_id!r} snapshot does not exist")

        source_target_field_count = raw.get("sourceTargetFieldCount")
        if (
            not isinstance(source_target_field_count, int)
            or isinstance(source_target_field_count, bool)
            or source_target_field_count <= 0
            or source_target_field_count > len(AUTOEVOLUTION_ARTEGA_GT_RULES_V1)
        ):
            raise ValueError(f"case {case_id!r} has invalid sourceTargetFieldCount")

        expected_outcome = raw.get("expectedOutcome")
        if expected_outcome not in {"SUCCESS", "FAIL"}:
            raise ValueError(f"case {case_id!r} has invalid expectedOutcome")

        expected_parsed = raw.get("expectedParsed")
        if not isinstance(expected_parsed, dict) or not expected_parsed:
            raise ValueError(f"case {case_id!r} requires expectedParsed")
        if any(not isinstance(attribute, str) or not attribute for attribute in expected_parsed):
            raise ValueError(f"case {case_id!r} has invalid expectedParsed attributes")

        expected_failure_contains = raw.get("expectedFailureContains")
        if expected_outcome == "FAIL":
            if not isinstance(expected_failure_contains, str) or not expected_failure_contains.strip():
                raise ValueError(f"case {case_id!r} requires expectedFailureContains")
        elif expected_failure_contains is not None:
            raise ValueError(f"case {case_id!r} SUCCESS cannot define expectedFailureContains")

        non_scalar_target_fields = tuple(raw.get("nonScalarTargetFields", ()))
        if any(not isinstance(field, str) or not field for field in non_scalar_target_fields):
            raise ValueError(f"case {case_id!r} has invalid nonScalarTargetFields")

        label_variants = raw.get("labelVariants", {})
        if not isinstance(label_variants, dict) or any(
            not isinstance(attribute, str)
            or not attribute
            or not isinstance(label, str)
            or not label
            for attribute, label in label_variants.items()
        ):
            raise ValueError(f"case {case_id!r} has invalid labelVariants")

        if expected_outcome == "SUCCESS":
            if source_target_field_count != len(AUTOEVOLUTION_ARTEGA_GT_RULES_V1):
                raise ValueError(f"case {case_id!r} SUCCESS must expose every artifact target field")
            if len(expected_parsed) != source_target_field_count:
                raise ValueError(f"case {case_id!r} SUCCESS gold facts must cover every target field")

        target_gold_count = len(expected_parsed) + len(non_scalar_target_fields)
        if target_gold_count > source_target_field_count:
            raise ValueError(f"case {case_id!r} gold facts exceed sourceTargetFieldCount")

        text = snapshot_path.read_text(encoding="utf-8")
        if f"SOURCE: {source_url}" not in text.splitlines()[:3]:
            raise ValueError(f"case {case_id!r} snapshot SOURCE header does not match sourceUrl")
        if not any(line.startswith("ACQUIRED: ") for line in text.splitlines()[:4]):
            raise ValueError(f"case {case_id!r} snapshot requires ACQUIRED header")

        cases.append(
            WebExtractionCorpusCase(
                id=case_id,
                manufacturer=manufacturer,
                source_url=source_url,
                snapshot_path=snapshot_path,
                source_target_field_count=source_target_field_count,
                expected_outcome=expected_outcome,
                expected_parsed=dict(expected_parsed),
                expected_failure_contains=expected_failure_contains,
                non_scalar_target_fields=non_scalar_target_fields,
                label_variants=dict(label_variants),
            )
        )

    return WebExtractionCorpus(version=version, artifact=artifact, cases=tuple(cases))


def _bounded_value(value: object, *, case_id: str, attribute: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"minValue", "maxValue"}:
        raise ValueError(
            f"bounded gold {case_id!r} attribute {attribute!r} requires minValue/maxValue"
        )
    minimum = value["minValue"]
    maximum = value["maxValue"]
    for name, bound in (("minValue", minimum), ("maxValue", maximum)):
        if isinstance(bound, bool) or not isinstance(bound, (int, float)):
            raise ValueError(f"bounded gold {case_id!r} {name} must be numeric")
        if not math.isfinite(float(bound)):
            raise ValueError(f"bounded gold {case_id!r} {name} must be finite")
    if float(minimum) > float(maximum):
        raise ValueError(f"bounded gold {case_id!r} minimum cannot exceed maximum")
    return {"minValue": minimum, "maxValue": maximum}


def load_web_extraction_bounded_gold(
    path: str | Path,
    base_dataset: WebExtractionCorpus,
) -> WebExtractionBoundedGold:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != WEB_EXTRACTION_BOUNDED_GOLD_SCHEMA:
        raise ValueError("unsupported web extraction bounded gold schema")

    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("bounded gold datasetVersion is required")
    if payload.get("baseDatasetVersion") != base_dataset.version:
        raise ValueError("bounded gold baseDatasetVersion does not match source-family corpus")
    artifact = payload.get("artifact")
    if artifact != "AUTOEVOLUTION_ARTEGA_GT_RULES_V2":
        raise ValueError("bounded gold artifact is unsupported")

    base_by_id = {case.id: case for case in base_dataset.cases}
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("bounded gold cases are required")

    expected_by_case: dict[str, dict[str, object]] = {}
    for raw in raw_cases:
        case_id = raw.get("id")
        if not isinstance(case_id, str) or case_id not in base_by_id:
            raise ValueError(f"bounded gold references unknown case {case_id!r}")
        if case_id in expected_by_case:
            raise ValueError(f"duplicate bounded gold case id {case_id!r}")
        expected = raw.get("expectedParsed")
        if not isinstance(expected, dict) or not expected:
            raise ValueError(f"bounded gold case {case_id!r} requires expectedParsed")

        base_case = base_by_id[case_id]
        expected_attributes = set(expected)
        if expected_attributes != set(base_case.non_scalar_target_fields):
            raise ValueError(
                f"bounded gold case {case_id!r} must cover exactly its non-scalar target fields"
            )
        expected_by_case[case_id] = {
            attribute: _bounded_value(value, case_id=case_id, attribute=attribute)
            for attribute, value in expected.items()
        }

    required_case_ids = {
        case.id for case in base_dataset.cases if case.non_scalar_target_fields
    }
    if set(expected_by_case) != required_case_ids:
        raise ValueError("bounded gold must cover every non-scalar source target case")

    return WebExtractionBoundedGold(
        version=version,
        base_dataset_version=base_dataset.version,
        artifact=artifact,
        expected_by_case=expected_by_case,
    )


def _field_comparison(
    parsed: dict[str, object],
    expected_parsed: dict[str, object],
) -> tuple[list[str], int]:
    incorrect_fields = sorted(
        attribute
        for attribute, actual in parsed.items()
        if attribute not in expected_parsed or expected_parsed[attribute] != actual
    )
    correct_fields = sum(
        attribute in expected_parsed and expected_parsed[attribute] == actual
        for attribute, actual in parsed.items()
    )
    return incorrect_fields, correct_fields


def _strict_report(
    dataset: WebExtractionCorpus,
    *,
    rules: tuple[WebFieldRule, ...],
    artifact: str,
    report_dataset_version: str,
    expected_overrides: dict[str, dict[str, object]] | None = None,
) -> dict[str, Any]:
    overrides = expected_overrides or {}
    results: list[dict[str, Any]] = []
    total_target_fields = 0
    total_emitted_fields = 0
    total_correct_fields = 0

    for case in dataset.cases:
        total_target_fields += case.source_target_field_count
        expected_parsed = {**case.expected_parsed, **overrides.get(case.id, {})}
        expected_outcome = "SUCCESS" if case.id in overrides else case.expected_outcome
        expected_failure_contains = None if case.id in overrides else case.expected_failure_contains
        text = case.snapshot_path.read_text(encoding="utf-8")
        try:
            extracted = extract_with_rules(text, rules)
        except ValueError as exc:
            error = str(exc)
            expected_match = (
                expected_outcome == "FAIL"
                and expected_failure_contains is not None
                and expected_failure_contains in error
            )
            results.append(
                {
                    "id": case.id,
                    "expectedOutcome": expected_outcome,
                    "actualOutcome": "FAIL",
                    "expectedOutcomeMatches": expected_match,
                    "emittedFieldCount": 0,
                    "correctFieldCount": 0,
                    "incorrectFields": [],
                    "error": error,
                }
            )
            continue

        parsed = {fact.attribute: fact.parsed_value for fact in extracted}
        incorrect_fields, correct_fields = _field_comparison(parsed, expected_parsed)
        emitted_fields = len(parsed)
        total_emitted_fields += emitted_fields
        total_correct_fields += correct_fields
        results.append(
            {
                "id": case.id,
                "expectedOutcome": expected_outcome,
                "actualOutcome": "SUCCESS",
                "expectedOutcomeMatches": expected_outcome == "SUCCESS",
                "emittedFieldCount": emitted_fields,
                "correctFieldCount": correct_fields,
                "incorrectFields": incorrect_fields,
                "error": None,
            }
        )

    total_cases = len(results)
    page_success_count = sum(result["actualOutcome"] == "SUCCESS" for result in results)
    explicit_failure_count = total_cases - page_success_count
    expected_outcome_matches = sum(bool(result["expectedOutcomeMatches"]) for result in results)
    fully_correct_page_count = sum(
        result["actualOutcome"] == "SUCCESS"
        and result["correctFieldCount"] == result["emittedFieldCount"]
        for result in results
    )

    return {
        "schema": "podium7.web-extraction-source-family-report.v1",
        "datasetVersion": report_dataset_version,
        "artifact": artifact,
        "totalCases": total_cases,
        "metrics": {
            "pageSuccessCount": page_success_count,
            "pageSuccessRate": _rate(page_success_count, total_cases),
            "explicitFailureCount": explicit_failure_count,
            "explicitFailureRate": _rate(explicit_failure_count, total_cases),
            "expectedOutcomeMatches": expected_outcome_matches,
            "expectedOutcomeMatchRate": _rate(expected_outcome_matches, total_cases),
            "fullyCorrectPageCount": fully_correct_page_count,
            "targetFieldCount": total_target_fields,
            "emittedFieldCount": total_emitted_fields,
            "correctFieldCount": total_correct_fields,
            "fieldPrecision": _rate(total_correct_fields, total_emitted_fields),
            "fieldRecall": _rate(total_correct_fields, total_target_fields),
        },
        "cases": results,
    }


def _partial_report(
    dataset: WebExtractionCorpus,
    *,
    rules: tuple[WebFieldRule, ...],
    artifact: str,
    report_dataset_version: str,
    expected_overrides: dict[str, dict[str, object]] | None = None,
) -> dict[str, Any]:
    overrides = expected_overrides or {}
    results: list[dict[str, Any]] = []
    total_target_fields = 0
    total_emitted_fields = 0
    total_correct_fields = 0
    total_issues = 0

    for case in dataset.cases:
        total_target_fields += case.source_target_field_count
        expected_parsed = {**case.expected_parsed, **overrides.get(case.id, {})}
        expected_outcome = "SUCCESS" if case.id in overrides else case.expected_outcome
        text = case.snapshot_path.read_text(encoding="utf-8")
        report = extract_with_rules_report(text, rules)
        parsed = {fact.attribute: fact.parsed_value for fact in report.facts}
        incorrect_fields, correct_fields = _field_comparison(parsed, expected_parsed)
        emitted_fields = len(parsed)
        issues = [
            {
                "attribute": issue.attribute,
                "label": issue.label,
                "code": issue.code,
                "message": issue.message,
                "rawValue": issue.raw_value,
            }
            for issue in report.issues
        ]

        total_emitted_fields += emitted_fields
        total_correct_fields += correct_fields
        total_issues += len(issues)
        results.append(
            {
                "id": case.id,
                "strictExpectedOutcome": expected_outcome,
                "emittedFieldCount": emitted_fields,
                "correctFieldCount": correct_fields,
                "incorrectFields": incorrect_fields,
                "issues": issues,
            }
        )

    total_cases = len(results)
    cases_with_issues = sum(bool(result["issues"]) for result in results)
    unresolved_target_fields = total_target_fields - total_correct_fields

    return {
        "schema": "podium7.web-extraction-partial-evidence-report.v1",
        "datasetVersion": report_dataset_version,
        "artifact": artifact,
        "totalCases": total_cases,
        "metrics": {
            "casesWithIssues": cases_with_issues,
            "casesWithoutIssues": total_cases - cases_with_issues,
            "issueCount": total_issues,
            "targetFieldCount": total_target_fields,
            "emittedFieldCount": total_emitted_fields,
            "correctFieldCount": total_correct_fields,
            "incorrectFieldCount": total_emitted_fields - total_correct_fields,
            "unresolvedTargetFieldCount": unresolved_target_fields,
            "fieldPrecision": _rate(total_correct_fields, total_emitted_fields),
            "fieldRecall": _rate(total_correct_fields, total_target_fields),
        },
        "cases": results,
    }


def evaluate_web_extraction_corpus(dataset: WebExtractionCorpus) -> dict[str, Any]:
    """Replay the historical source-family V1 artifact and expectations."""
    return _strict_report(
        dataset,
        rules=AUTOEVOLUTION_ARTEGA_GT_RULES_V1,
        artifact=dataset.artifact,
        report_dataset_version=dataset.version,
    )


def evaluate_web_extraction_partial_evidence_corpus(
    dataset: WebExtractionCorpus,
) -> dict[str, Any]:
    """Replay the historical V1 partial-evidence characterization."""
    return _partial_report(
        dataset,
        rules=AUTOEVOLUTION_ARTEGA_GT_RULES_V1,
        artifact=dataset.artifact,
        report_dataset_version=dataset.version,
    )


def evaluate_web_extraction_bounded_corpus(
    dataset: WebExtractionCorpus,
    bounded_gold: WebExtractionBoundedGold,
) -> dict[str, Any]:
    return _strict_report(
        dataset,
        rules=AUTOEVOLUTION_ARTEGA_GT_RULES_V2,
        artifact=bounded_gold.artifact,
        report_dataset_version=f"{dataset.version}+{bounded_gold.version}",
        expected_overrides=bounded_gold.expected_by_case,
    )


def evaluate_web_extraction_bounded_partial_evidence_corpus(
    dataset: WebExtractionCorpus,
    bounded_gold: WebExtractionBoundedGold,
) -> dict[str, Any]:
    return _partial_report(
        dataset,
        rules=AUTOEVOLUTION_ARTEGA_GT_RULES_V2,
        artifact=bounded_gold.artifact,
        report_dataset_version=f"{dataset.version}+{bounded_gold.version}",
        expected_overrides=bounded_gold.expected_by_case,
    )


__all__ = [
    "WEB_EXTRACTION_BOUNDED_GOLD_SCHEMA",
    "WEB_EXTRACTION_CORPUS_SCHEMA",
    "WebExtractionBoundedGold",
    "WebExtractionCorpus",
    "WebExtractionCorpusCase",
    "evaluate_web_extraction_bounded_corpus",
    "evaluate_web_extraction_bounded_partial_evidence_corpus",
    "evaluate_web_extraction_corpus",
    "evaluate_web_extraction_partial_evidence_corpus",
    "load_web_extraction_bounded_gold",
    "load_web_extraction_corpus",
]
