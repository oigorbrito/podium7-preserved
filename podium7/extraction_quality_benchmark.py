from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any


REPORT_SCHEMA = "podium7.extraction-quality-benchmark.v1"


@dataclass(frozen=True)
class ExtractionBenchmarkCase:
    case_id: str
    expected_fields: Mapping[str, Any]
    observed_fields: Mapping[str, Any]
    required_fields: frozenset[str]
    evidence_by_field: Mapping[str, Sequence[str]]
    schema_valid: bool
    canonical_written_fields: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be non-empty text")
        if not isinstance(self.schema_valid, bool):
            raise ValueError("schema_valid must be boolean")
        if not self.expected_fields:
            raise ValueError("expected_fields cannot be empty")
        if any(not isinstance(key, str) or not key.strip() for key in self.expected_fields):
            raise ValueError("expected field names must be non-empty text")
        if any(not isinstance(key, str) or not key.strip() for key in self.observed_fields):
            raise ValueError("observed field names must be non-empty text")
        if not self.required_fields <= set(self.expected_fields):
            raise ValueError("required_fields must be a subset of expected_fields")
        for field_name, evidence_ids in self.evidence_by_field.items():
            if field_name not in self.observed_fields:
                raise ValueError("evidence may only reference observed fields")
            if isinstance(evidence_ids, (str, bytes)) or not isinstance(evidence_ids, Sequence):
                raise ValueError("field evidence must be an array of evidence ids")
            if any(not isinstance(item, str) or not item.strip() for item in evidence_ids):
                raise ValueError("field evidence ids must be non-empty text")
        if any(not isinstance(field_name, str) or not field_name.strip() for field_name in self.canonical_written_fields):
            raise ValueError("canonical_written_fields must contain non-empty field names")


def _dimension(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "text"
    if isinstance(value, list):
        return "array"
    if isinstance(value, Mapping):
        return "object"
    return type(value).__name__


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def evaluate_extraction_cases(cases: Iterable[ExtractionBenchmarkCase]) -> dict[str, Any]:
    case_list = tuple(cases)
    if not case_list:
        raise ValueError("at least one extraction benchmark case is required")
    if any(not isinstance(case, ExtractionBenchmarkCase) for case in case_list):
        raise ValueError("all benchmark items must be ExtractionBenchmarkCase instances")
    case_ids = [case.case_id for case in case_list]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("case_id values must be unique")

    total_expected = total_observed = correct = omitted = hallucinated = 0
    required_total = required_present = 0
    evidence_linked_observed = 0
    array_total = array_correct = 0
    schema_valid_count = 0
    canonical_writes = unsupported_canonical_writes = 0
    dimensions: dict[str, Counter[str]] = {}
    widths: dict[int, Counter[str]] = {}
    observations: list[dict[str, Any]] = []

    for case in case_list:
        expected = dict(case.expected_fields)
        observed = dict(case.observed_fields)
        expected_names = set(expected)
        observed_names = set(observed)
        correct_names = {name for name in expected_names & observed_names if observed[name] == expected[name]}
        omitted_names = expected_names - observed_names
        hallucinated_names = observed_names - expected_names
        linked_names = {
            name for name in observed_names
            if case.evidence_by_field.get(name)
        }

        unsupported_written = {
            name for name in case.canonical_written_fields
            if name not in correct_names or name not in linked_names
        }

        total_expected += len(expected_names)
        total_observed += len(observed_names)
        correct += len(correct_names)
        omitted += len(omitted_names)
        hallucinated += len(hallucinated_names)
        required_total += len(case.required_fields)
        required_present += len(case.required_fields & observed_names)
        evidence_linked_observed += len(linked_names)
        schema_valid_count += int(case.schema_valid)
        canonical_writes += len(case.canonical_written_fields)
        unsupported_canonical_writes += len(unsupported_written)

        width_counter = widths.setdefault(len(expected_names), Counter())
        width_counter["cases"] += 1
        width_counter["expected"] += len(expected_names)
        width_counter["correct"] += len(correct_names)

        for name, expected_value in expected.items():
            dimension = _dimension(expected_value)
            counter = dimensions.setdefault(dimension, Counter())
            counter["expected"] += 1
            if name in observed_names:
                counter["observed"] += 1
                if name in correct_names:
                    counter["correct"] += 1
            if isinstance(expected_value, list):
                array_total += 1
                if name in correct_names:
                    array_correct += 1

        observations.append(
            {
                "caseId": case.case_id,
                "schemaWidth": len(expected_names),
                "schemaValid": case.schema_valid,
                "correctFields": sorted(correct_names),
                "omittedFields": sorted(omitted_names),
                "hallucinatedFields": sorted(hallucinated_names),
                "evidenceLinkedObservedFields": sorted(linked_names),
                "unsupportedCanonicalWrites": sorted(unsupported_written),
            }
        )

    by_dimension = {
        dimension: {
            "expected": counter["expected"],
            "observed": counter["observed"],
            "correct": counter["correct"],
            "correctness": _safe_rate(counter["correct"], counter["expected"]),
        }
        for dimension, counter in sorted(dimensions.items())
    }
    by_schema_width = {
        str(width): {
            "caseCount": counter["cases"],
            "expectedFieldCount": counter["expected"],
            "correctFieldCount": counter["correct"],
            "fieldCorrectness": _safe_rate(counter["correct"], counter["expected"]),
        }
        for width, counter in sorted(widths.items())
    }

    return {
        "schema": REPORT_SCHEMA,
        "metrics": {
            "caseCount": len(case_list),
            "schemaValidRate": _safe_rate(schema_valid_count, len(case_list)),
            "fieldCorrectness": _safe_rate(correct, total_expected),
            "requiredFieldRecall": _safe_rate(required_present, required_total),
            "hallucinatedFieldRate": _safe_rate(hallucinated, total_observed),
            "omittedFieldRate": _safe_rate(omitted, total_expected),
            "arrayAlignmentAccuracy": _safe_rate(array_correct, array_total),
            "evidenceLinkedFieldRate": _safe_rate(evidence_linked_observed, total_observed),
            "unsupportedCanonicalWriteRate": _safe_rate(unsupported_canonical_writes, canonical_writes),
            "unsupportedCanonicalWriteCount": unsupported_canonical_writes,
        },
        "byDimension": by_dimension,
        "bySchemaWidth": by_schema_width,
        "observations": observations,
    }


__all__ = ["ExtractionBenchmarkCase", "REPORT_SCHEMA", "evaluate_extraction_cases"]
