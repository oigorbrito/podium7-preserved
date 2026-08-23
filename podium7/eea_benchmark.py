from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .eea_source import extract_eea_record, extract_eea_record_report, load_eea_response


EEA_CORPUS_SCHEMA = "podium7.eea-source-family.v1"
EEA_ARTIFACT = "EEA_CO2_CARS_2025_V1"
EEA_REPORT_SCHEMA = "podium7.eea-source-family-report.v1"
_SUPPORTED_FACTS = {"power", "displacement", "fuel_type"}
_IDENTITY_FIELDS = {
    "member_state",
    "make",
    "commercial_name",
    "manufacturer",
    "type_approval_number",
    "vehicle_type",
    "variant",
    "version",
    "registration_year",
    "status",
}
_REGULATORY_FIELDS = {
    "mass_in_running_order_kg",
    "engine_capacity_cm3",
    "engine_power_kw",
    "fuel_type",
    "fuel_mode",
    "wltp_co2_g_km",
    "electric_energy_consumption_wh_km",
}


@dataclass(frozen=True)
class EeaCorpusCase:
    id: str
    source_record_id: int
    source_target_field_count: int
    expected_identity: dict[str, object]
    expected_regulatory: dict[str, object]
    expected_facts: dict[str, object]


@dataclass(frozen=True)
class EeaCorpus:
    version: str
    artifact: str
    source_url: str
    snapshot_path: Path
    snapshot_sha256: str
    snapshot_size_bytes: int
    cases: tuple[EeaCorpusCase, ...]


def _rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def _required_nonempty_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required")
    return value.strip()


def _required_positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _validate_expected_object(
    value: object,
    *,
    label: str,
    expected_keys: set[str],
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if set(value) != expected_keys:
        raise ValueError(f"{label} must classify exactly {sorted(expected_keys)!r}")
    return dict(value)


def load_eea_corpus(path: str | Path) -> EeaCorpus:
    dataset_path = Path(path).resolve()
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if payload.get("schema") != EEA_CORPUS_SCHEMA:
        raise ValueError("unsupported EEA source-family corpus schema")
    if payload.get("artifact") != EEA_ARTIFACT:
        raise ValueError("unsupported EEA source-family artifact")

    version = _required_nonempty_text(payload.get("datasetVersion"), "datasetVersion")
    source = payload.get("source")
    if not isinstance(source, dict):
        raise ValueError("EEA corpus source object is required")

    source_url = _required_nonempty_text(source.get("sourceUrl"), "source.sourceUrl")
    parsed_url = urlsplit(source_url)
    if parsed_url.scheme != "https" or parsed_url.hostname != "discodata.eea.europa.eu":
        raise ValueError("EEA sourceUrl must use the official Discodata HTTPS host")
    if parsed_url.fragment:
        raise ValueError("EEA sourceUrl must not contain a fragment")

    snapshot = _required_nonempty_text(source.get("snapshot"), "source.snapshot")
    repo_root = dataset_path.parent.parent
    snapshot_path = (repo_root / snapshot).resolve()
    try:
        snapshot_path.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("EEA snapshot escapes repository root") from exc
    if not snapshot_path.is_file():
        raise ValueError("EEA snapshot does not exist")

    expected_sha = _required_nonempty_text(source.get("snapshotSha256"), "source.snapshotSha256")
    if len(expected_sha) != 64 or any(character not in "0123456789abcdef" for character in expected_sha):
        raise ValueError("source.snapshotSha256 must be lowercase SHA-256 hex")
    expected_size = _required_positive_int(source.get("snapshotSizeBytes"), "source.snapshotSizeBytes")

    snapshot_bytes = snapshot_path.read_bytes()
    actual_sha = hashlib.sha256(snapshot_bytes).hexdigest()
    if actual_sha != expected_sha:
        raise ValueError("EEA snapshot SHA-256 does not match corpus pin")
    if len(snapshot_bytes) != expected_size:
        raise ValueError("EEA snapshot byte size does not match corpus pin")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("EEA corpus cases are required")

    cases: list[EeaCorpusCase] = []
    seen_case_ids: set[str] = set()
    seen_record_ids: set[int] = set()
    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise ValueError("EEA corpus case must be an object")
        case_id = _required_nonempty_text(raw.get("id"), "case.id")
        if case_id in seen_case_ids:
            raise ValueError(f"duplicate EEA case id {case_id!r}")
        seen_case_ids.add(case_id)

        record_id = _required_positive_int(raw.get("sourceRecordId"), f"case {case_id} sourceRecordId")
        if record_id in seen_record_ids:
            raise ValueError(f"duplicate EEA sourceRecordId {record_id}")
        seen_record_ids.add(record_id)

        expected_identity = _validate_expected_object(
            raw.get("expectedIdentity"),
            label=f"case {case_id} expectedIdentity",
            expected_keys=_IDENTITY_FIELDS,
        )
        expected_regulatory = _validate_expected_object(
            raw.get("expectedRegulatory"),
            label=f"case {case_id} expectedRegulatory",
            expected_keys=_REGULATORY_FIELDS,
        )

        expected_facts = raw.get("expectedFacts")
        if not isinstance(expected_facts, dict) or not expected_facts:
            raise ValueError(f"case {case_id} expectedFacts is required")
        if not set(expected_facts).issubset(_SUPPORTED_FACTS):
            raise ValueError(f"case {case_id} has unsupported expected fact")

        target_count = _required_positive_int(
            raw.get("sourceTargetFieldCount"),
            f"case {case_id} sourceTargetFieldCount",
        )
        if target_count != len(expected_facts):
            raise ValueError(f"case {case_id} target count must equal independently classified facts")

        cases.append(
            EeaCorpusCase(
                id=case_id,
                source_record_id=record_id,
                source_target_field_count=target_count,
                expected_identity=expected_identity,
                expected_regulatory=expected_regulatory,
                expected_facts=dict(expected_facts),
            )
        )

    rows = load_eea_response(snapshot_bytes)
    snapshot_ids = {row["ID"] for row in rows}
    if snapshot_ids != seen_record_ids:
        raise ValueError("EEA snapshot record IDs must match corpus cases exactly")

    return EeaCorpus(
        version=version,
        artifact=EEA_ARTIFACT,
        source_url=source_url,
        snapshot_path=snapshot_path,
        snapshot_sha256=expected_sha,
        snapshot_size_bytes=expected_size,
        cases=tuple(cases),
    )


def _compare(actual: dict[str, object], expected: dict[str, object]) -> tuple[int, list[str]]:
    incorrect = sorted(
        attribute
        for attribute, value in actual.items()
        if attribute not in expected or expected[attribute] != value
    )
    correct = sum(
        attribute in expected and expected[attribute] == value
        for attribute, value in actual.items()
    )
    return correct, incorrect


def _identity_dict(report: Any) -> dict[str, object]:
    value = asdict(report.identity)
    value.pop("source_record_id")
    return value


def evaluate_eea_corpus(corpus: EeaCorpus, *, partial_evidence: bool = False) -> dict[str, Any]:
    rows = {row["ID"]: row for row in load_eea_response(corpus.snapshot_path.read_bytes())}
    target_fields = sum(case.source_target_field_count for case in corpus.cases)
    emitted_fields = 0
    correct_fields = 0
    issue_count = 0
    results: list[dict[str, Any]] = []

    for case in corpus.cases:
        row = rows[case.source_record_id]
        if partial_evidence:
            report = extract_eea_record_report(row)
        else:
            try:
                report = extract_eea_record(row)
            except ValueError as exc:
                results.append(
                    {
                        "id": case.id,
                        "sourceRecordId": case.source_record_id,
                        "actualOutcome": "FAIL",
                        "identityMatches": False,
                        "regulatoryEvidenceMatches": False,
                        "emittedFieldCount": 0,
                        "correctFieldCount": 0,
                        "incorrectFields": [],
                        "issueCodes": [],
                        "error": str(exc),
                    }
                )
                continue

        actual_facts = {fact.attribute: fact.normalized_value for fact in report.facts}
        correct, incorrect = _compare(actual_facts, case.expected_facts)
        identity_matches = _identity_dict(report) == case.expected_identity
        regulatory_matches = asdict(report.regulatory) == case.expected_regulatory
        emitted_fields += len(actual_facts)
        correct_fields += correct
        issue_count += len(report.issues)
        results.append(
            {
                "id": case.id,
                "sourceRecordId": case.source_record_id,
                "actualOutcome": "SUCCESS" if not report.issues else "PARTIAL",
                "identityMatches": identity_matches,
                "regulatoryEvidenceMatches": regulatory_matches,
                "emittedFieldCount": len(actual_facts),
                "correctFieldCount": correct,
                "incorrectFields": incorrect,
                "issueCodes": [issue.code for issue in report.issues],
                "error": None,
            }
        )

    if partial_evidence:
        clean_cases = sum(not result["issueCodes"] for result in results)
        unresolved = target_fields - correct_fields
        return {
            "schema": EEA_REPORT_SCHEMA,
            "datasetVersion": corpus.version,
            "artifact": corpus.artifact,
            "mode": "partial-evidence",
            "totalCases": len(corpus.cases),
            "source": {
                "url": corpus.source_url,
                "snapshotSha256": corpus.snapshot_sha256,
                "snapshotSizeBytes": corpus.snapshot_size_bytes,
            },
            "metrics": {
                "casesWithoutIssues": clean_cases,
                "casesWithIssues": len(corpus.cases) - clean_cases,
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

    strict_successes = sum(
        result["actualOutcome"] == "SUCCESS"
        and result["identityMatches"]
        and result["regulatoryEvidenceMatches"]
        and not result["incorrectFields"]
        and result["correctFieldCount"]
        == next(case.source_target_field_count for case in corpus.cases if case.id == result["id"])
        for result in results
    )
    return {
        "schema": EEA_REPORT_SCHEMA,
        "datasetVersion": corpus.version,
        "artifact": corpus.artifact,
        "mode": "strict",
        "totalCases": len(corpus.cases),
        "source": {
            "url": corpus.source_url,
            "snapshotSha256": corpus.snapshot_sha256,
            "snapshotSizeBytes": corpus.snapshot_size_bytes,
        },
        "metrics": {
            "strictSuccessCount": strict_successes,
            "strictSuccessRate": _rate(strict_successes, len(corpus.cases)),
            "targetFieldCount": target_fields,
            "emittedFieldCount": emitted_fields,
            "correctFieldCount": correct_fields,
            "incorrectFieldCount": emitted_fields - correct_fields,
            "fieldPrecision": _rate(correct_fields, emitted_fields),
            "fieldRecall": _rate(correct_fields, target_fields),
        },
        "cases": results,
    }
