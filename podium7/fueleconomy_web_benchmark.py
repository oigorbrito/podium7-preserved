from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .web_extraction import (
    FUELECONOMY_GOV_VEHICLE_RULES_V1,
    extract_with_rules,
    extract_with_rules_report,
)


FUELECONOMY_CORPUS_SCHEMA = "podium7.web-extraction-fueleconomy-source-family.v1"
FUELECONOMY_ARTIFACT = "FUELECONOMY_GOV_VEHICLE_RULES_V1"
FUELECONOMY_RULE_NAMESPACE = "fueleconomy_gov"


@dataclass(frozen=True)
class FuelEconomyCorpusCase:
    id: str
    source_url: str
    snapshot_path: Path
    source_target_field_count: int
    expected_outcome: str
    expected_parsed: dict[str, object]
    expected_failure_contains: str | None
    unsupported_target_fields: tuple[str, ...]


@dataclass(frozen=True)
class FuelEconomyCorpus:
    version: str
    artifact: str
    cases: tuple[FuelEconomyCorpusCase, ...]


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def load_fueleconomy_corpus(path: str | Path) -> FuelEconomyCorpus:
    dataset_path = Path(path).resolve()
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if payload.get("schema") != FUELECONOMY_CORPUS_SCHEMA:
        raise ValueError("unsupported FuelEconomy web corpus schema")

    version = payload.get("datasetVersion")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("FuelEconomy datasetVersion is required")
    if payload.get("artifact") != FUELECONOMY_ARTIFACT:
        raise ValueError("FuelEconomy corpus artifact is unsupported")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("FuelEconomy corpus cases are required")

    repo_root = dataset_path.parent.parent
    artifact_attributes = {rule.attribute for rule in FUELECONOMY_GOV_VEHICLE_RULES_V1}
    cases: list[FuelEconomyCorpusCase] = []
    seen_ids: set[str] = set()

    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise ValueError("FuelEconomy corpus case must be an object")
        case_id = raw.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("FuelEconomy corpus case id is required")
        if case_id in seen_ids:
            raise ValueError(f"duplicate FuelEconomy case id {case_id!r}")
        seen_ids.add(case_id)

        source_url = raw.get("sourceUrl")
        if (
            not isinstance(source_url, str)
            or not source_url.startswith("https://www.fueleconomy.gov/")
        ):
            raise ValueError(f"case {case_id!r} requires a FuelEconomy.gov HTTPS sourceUrl")

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

        target_count = raw.get("sourceTargetFieldCount")
        if (
            not isinstance(target_count, int)
            or isinstance(target_count, bool)
            or target_count != len(FUELECONOMY_GOV_VEHICLE_RULES_V1)
        ):
            raise ValueError(f"case {case_id!r} has invalid sourceTargetFieldCount")

        expected_outcome = raw.get("expectedOutcome")
        if expected_outcome not in {"SUCCESS", "FAIL"}:
            raise ValueError(f"case {case_id!r} has invalid expectedOutcome")

        expected_parsed = raw.get("expectedParsed")
        if not isinstance(expected_parsed, dict) or not expected_parsed:
            raise ValueError(f"case {case_id!r} requires expectedParsed")
        if not set(expected_parsed).issubset(artifact_attributes):
            raise ValueError(f"case {case_id!r} has unknown expectedParsed attribute")

        unsupported = raw.get("unsupportedTargetFields", [])
        if not isinstance(unsupported, list) or any(
            not isinstance(attribute, str) or attribute not in artifact_attributes
            for attribute in unsupported
        ):
            raise ValueError(f"case {case_id!r} has invalid unsupportedTargetFields")
        if len(set(unsupported)) != len(unsupported):
            raise ValueError(f"case {case_id!r} duplicates unsupportedTargetFields")
        if set(unsupported) & set(expected_parsed):
            raise ValueError(f"case {case_id!r} overlaps parsed and unsupported targets")
        if len(expected_parsed) + len(unsupported) != target_count:
            raise ValueError(f"case {case_id!r} gold must classify every source target field")

        expected_failure = raw.get("expectedFailureContains")
        if expected_outcome == "SUCCESS":
            if unsupported or expected_failure is not None:
                raise ValueError(f"case {case_id!r} SUCCESS cannot define unsupported/failure gold")
        else:
            if not unsupported:
                raise ValueError(f"case {case_id!r} FAIL requires unsupportedTargetFields")
            if not isinstance(expected_failure, str) or not expected_failure.strip():
                raise ValueError(f"case {case_id!r} FAIL requires expectedFailureContains")

        lines = snapshot_path.read_text(encoding="utf-8").splitlines()
        if f"SOURCE: {source_url}" not in lines[:3]:
            raise ValueError(f"case {case_id!r} snapshot SOURCE header does not match sourceUrl")
        if "ACQUIRED: 2026-08-23" not in lines[:4]:
            raise ValueError(f"case {case_id!r} snapshot requires acquisition date")

        cases.append(
            FuelEconomyCorpusCase(
                id=case_id,
                source_url=source_url,
                snapshot_path=snapshot_path,
                source_target_field_count=target_count,
                expected_outcome=expected_outcome,
                expected_parsed=dict(expected_parsed),
                expected_failure_contains=expected_failure,
                unsupported_target_fields=tuple(unsupported),
            )
        )

    return FuelEconomyCorpus(version=version, artifact=FUELECONOMY_ARTIFACT, cases=tuple(cases))


def _compare(parsed: dict[str, object], expected: dict[str, object]) -> tuple[int, list[str]]:
    incorrect = sorted(
        attribute
        for attribute, value in parsed.items()
        if attribute not in expected or expected[attribute] != value
    )
    correct = sum(
        attribute in expected and expected[attribute] == value
        for attribute, value in parsed.items()
    )
    return correct, incorrect


def evaluate_fueleconomy_corpus(
    corpus: FuelEconomyCorpus,
    *,
    partial_evidence: bool = False,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    target_fields = sum(case.source_target_field_count for case in corpus.cases)
    emitted_fields = 0
    correct_fields = 0
    issue_count = 0

    for case in corpus.cases:
        text = case.snapshot_path.read_text(encoding="utf-8")
        if partial_evidence:
            report = extract_with_rules_report(
                text,
                FUELECONOMY_GOV_VEHICLE_RULES_V1,
                rule_namespace=FUELECONOMY_RULE_NAMESPACE,
            )
            parsed = {fact.attribute: fact.parsed_value for fact in report.facts}
            correct, incorrect = _compare(parsed, case.expected_parsed)
            emitted_fields += len(parsed)
            correct_fields += correct
            issue_count += len(report.issues)
            results.append(
                {
                    "id": case.id,
                    "emittedFieldCount": len(parsed),
                    "correctFieldCount": correct,
                    "incorrectFields": incorrect,
                    "issueCodes": [issue.code for issue in report.issues],
                    "issueAttributes": [issue.attribute for issue in report.issues],
                }
            )
            continue

        try:
            facts = extract_with_rules(
                text,
                FUELECONOMY_GOV_VEHICLE_RULES_V1,
                rule_namespace=FUELECONOMY_RULE_NAMESPACE,
            )
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

        parsed = {fact.attribute: fact.parsed_value for fact in facts}
        correct, incorrect = _compare(parsed, case.expected_parsed)
        emitted_fields += len(parsed)
        correct_fields += correct
        results.append(
            {
                "id": case.id,
                "expectedOutcome": case.expected_outcome,
                "actualOutcome": "SUCCESS",
                "expectedOutcomeMatches": case.expected_outcome == "SUCCESS",
                "emittedFieldCount": len(parsed),
                "correctFieldCount": correct,
                "incorrectFields": incorrect,
                "error": None,
            }
        )

    if partial_evidence:
        unresolved = target_fields - correct_fields
        cases_with_issues = sum(bool(result["issueCodes"]) for result in results)
        return {
            "schema": "podium7.web-extraction-fueleconomy-report.v1",
            "datasetVersion": corpus.version,
            "artifact": corpus.artifact,
            "mode": "partial-evidence",
            "totalCases": len(corpus.cases),
            "metrics": {
                "casesWithoutIssues": len(corpus.cases) - cases_with_issues,
                "casesWithIssues": cases_with_issues,
                "issueCount": issue_count,
                "targetFieldCount": target_fields,
                "emittedFieldCount": emitted_fields,
                "correctFieldCount": correct_fields,
                "incorrectFieldCount": emitted_fields - correct_fields,
                "unresolvedTargetFieldCount": unresolved,
                "fieldPrecision": _rate(correct_fields, emitted_fields),
                "retainedFieldRecall": _rate(correct_fields, target_fields),
            },
            "cases": results,
        }

    successes = sum(result["actualOutcome"] == "SUCCESS" for result in results)
    expected_matches = sum(bool(result["expectedOutcomeMatches"]) for result in results)
    return {
        "schema": "podium7.web-extraction-fueleconomy-report.v1",
        "datasetVersion": corpus.version,
        "artifact": corpus.artifact,
        "mode": "strict",
        "totalCases": len(corpus.cases),
        "metrics": {
            "pageSuccessCount": successes,
            "pageSuccessRate": _rate(successes, len(corpus.cases)),
            "explicitFailureCount": len(corpus.cases) - successes,
            "expectedOutcomeMatches": expected_matches,
            "expectedOutcomeMatchRate": _rate(expected_matches, len(corpus.cases)),
            "targetFieldCount": target_fields,
            "emittedFieldCount": emitted_fields,
            "correctFieldCount": correct_fields,
            "fieldPrecision": _rate(correct_fields, emitted_fields),
            "fieldRecall": _rate(correct_fields, target_fields),
        },
        "cases": results,
    }
