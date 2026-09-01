import json
from pathlib import Path
import tempfile
import unittest

from podium7.operational_provenance import (
    BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION,
    BLOCK_NO_UNIQUE_COMMON_SOURCE,
    BLOCK_UNKNOWN_CASE_SOURCE,
    OperationalProvenanceBlock,
    measure_operational_provenance_eligibility,
    unique_source_for_record,
)


ROOT = Path(__file__).resolve().parents[1]
V3_DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


def _write(payload: dict) -> Path:
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
    with handle:
        json.dump(payload, handle)
    return Path(handle.name)


class OperationalProvenanceEligibilityTests(unittest.TestCase):
    def test_measurement_separates_explicit_single_source_and_blocked_records(self) -> None:
        payload = {
            "schema": "podium7.catalog-identity-golden.v1",
            "datasetVersion": "operational-provenance-test-1",
            "sources": [
                {"id": "source-a", "url": "https://example.com/a"},
                {"id": "source-b", "url": "https://example.com/b"},
            ],
            "cases": [
                {
                    "id": "explicit",
                    "expected": "NO_MATCH",
                    "left": {"make": "Example", "model": "One", "generation": "A"},
                    "right": {"make": "Example", "model": "One", "generation": "B"},
                    "sourceIds": ["source-b", "source-a"],
                    "fieldSourceIds": {
                        "left": {"make": ["source-a"], "model": ["source-a"], "generation": ["source-a"]},
                        "right": {"make": ["source-b"], "model": ["source-b"], "generation": ["source-b"]},
                    },
                    "rationale": "explicit field attribution",
                },
                {
                    "id": "single-source",
                    "expected": "MATCH",
                    "left": {"make": "Example", "model": "Solo"},
                    "right": {"make": "Example", "model": "Solo"},
                    "sourceIds": ["source-a"],
                    "rationale": "sole source has no source-selection ambiguity",
                },
                {
                    "id": "blocked",
                    "expected": "REVIEW",
                    "left": {"make": "Example", "model": "Blocked"},
                    "right": {"make": "Example", "model": "Blocked"},
                    "sourceIds": ["source-a", "source-b"],
                    "rationale": "multiple sources without field attribution remain blocked",
                },
            ],
        }
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)

        report = measure_operational_provenance_eligibility((path,))
        summary = report["summary"]
        self.assertEqual(summary["records"], 6)
        self.assertEqual(summary["replayableRecords"], 4)
        self.assertEqual(summary["blockedRecords"], 2)
        self.assertEqual(
            summary["replayableByMethod"],
            {"EXPLICIT_FIELD_ATTRIBUTION": 2, "SOLE_CASE_SOURCE": 2},
        )
        self.assertEqual(
            summary["blockedByReasonCode"],
            {BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION: 2},
        )
        explicit = [item for item in report["records"] if item["caseId"] == "explicit"]
        self.assertEqual([item["sourceId"] for item in explicit], ["source-a", "source-b"])
        blocked = [item for item in report["records"] if item["caseId"] == "blocked"]
        self.assertTrue(all(item["reasonCode"] == BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION for item in blocked))

    def test_reason_code_does_not_depend_on_case_id_punctuation(self) -> None:
        case = {
            "id": "case.with.dot",
            "left": {"make": "Example", "model": "Road"},
            "right": {"make": "Example", "model": "Road"},
            "sourceIds": ["unknown-source"],
        }

        with self.assertRaises(OperationalProvenanceBlock) as caught:
            unique_source_for_record(case, side="left", known_sources={"source-a"})

        self.assertEqual(caught.exception.reason_code, BLOCK_UNKNOWN_CASE_SOURCE)
        self.assertEqual(str(caught.exception), "case 'case.with.dot' references unknown source ids")

    def test_valid_per_field_multisource_provenance_remains_blocked_without_common_source(self) -> None:
        payload = {
            "schema": "podium7.catalog-identity-golden.v1",
            "datasetVersion": "operational-provenance-multisource-1",
            "sources": [
                {"id": "source-a", "url": "https://example.com/a"},
                {"id": "source-b", "url": "https://example.com/b"},
            ],
            "cases": [
                {
                    "id": "well-attributed-composite",
                    "expected": "MATCH",
                    "left": {"make": "Example", "model": "Road", "generation": "G1"},
                    "right": {"make": "Example", "model": "Road", "generation": "G1"},
                    "sourceIds": ["source-a", "source-b"],
                    "fieldSourceIds": {
                        "left": {"make": ["source-a"], "model": ["source-a"], "generation": ["source-b"]},
                        "right": {"make": ["source-a"], "model": ["source-a"], "generation": ["source-b"]},
                    },
                    "rationale": "valid field-level provenance intentionally has no single common source",
                }
            ],
        }
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)

        report = measure_operational_provenance_eligibility((path,))
        self.assertEqual(report["summary"]["replayableRecords"], 0)
        self.assertEqual(report["summary"]["blockedRecords"], 2)
        self.assertEqual(
            report["summary"]["blockedByReasonCode"],
            {BLOCK_NO_UNIQUE_COMMON_SOURCE: 2},
        )

    def test_retained_v3_reports_12_of_72_replayable_without_inference(self) -> None:
        report = measure_operational_provenance_eligibility(V3_DATASETS)
        summary = report["summary"]
        self.assertEqual(summary["cases"], 36)
        self.assertEqual(summary["records"], 72)
        self.assertEqual(summary["replayableRecords"], 12)
        self.assertEqual(summary["blockedRecords"], 60)
        self.assertEqual(summary["replayableRate"], 12 / 72)
        self.assertEqual(summary["replayableByMethod"], {"SOLE_CASE_SOURCE": 12})
        self.assertEqual(
            summary["blockedByReasonCode"],
            {BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION: 60},
        )
        self.assertTrue(all(item["method"] == "SOLE_CASE_SOURCE" for item in report["records"] if item["replayable"]))
        self.assertTrue(all("multiple sourceIds" in item["reason"] for item in report["records"] if not item["replayable"]))


if __name__ == "__main__":
    unittest.main()
