from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .web_extraction import AUTOEVOLUTION_ARTEGA_GT_RULES, extract_with_rules


WEB_EXTRACTION_CORPUS_SCHEMA = "podium7.web-extraction-source-family-corpus.v1"


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
            or source_target_field_count > len(AUTOEVOLUTION_ARTEGA_GT_RULES)
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
            if source_target_field_count != len(AUTOEVOLUTION_ARTEGA_GT_RULES):
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


def evaluate_web_extraction_corpus(dataset: WebExtractionCorpus) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    total_target_fields = 0
    total_emitted_fields = 0
    total_correct_fields = 0

    for case in dataset.cases:
        total_target_fields += case.source_target_field_count
        text = case.snapshot_path.read_text(encoding="utf-8")
        try:
            extracted = extract_with_rules(text, AUTOEVOLUTION_ARTEGA_GT_RULES)
        except ValueError as exc:
            error = str(exc)
            expected_match = (
                case.expected_outcome == "FAIL"
                and case.expected_failure_contains is not None
                and case.expected_failure_contains in error
            )
            results.append(
                {
                    "id": case.id,
                    "expectedOutcome": case.expected_outcome,
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
        incorrect_fields = sorted(
            attribute
            for attribute, actual in parsed.items()
            if attribute not in case.expected_parsed or case.expected_parsed[attribute] != actual
        )
        correct_fields = sum(
            attribute in case.expected_parsed and case.expected_parsed[attribute] == actual
            for attribute, actual in parsed.items()
        )
        emitted_fields = len(parsed)
        total_emitted_fields += emitted_fields
        total_correct_fields += correct_fields
        results.append(
            {
                "id": case.id,
                "expectedOutcome": case.expected_outcome,
                "actualOutcome": "SUCCESS",
                "expectedOutcomeMatches": case.expected_outcome == "SUCCESS",
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
        "datasetVersion": dataset.version,
        "artifact": dataset.artifact,
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


__all__ = [
    "WEB_EXTRACTION_CORPUS_SCHEMA",
    "WebExtractionCorpus",
    "WebExtractionCorpusCase",
    "evaluate_web_extraction_corpus",
    "load_web_extraction_corpus",
]
