import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog_operational import (
    build_source_backed_operational_records,
    measure_operational_provenance_eligibility,
)


ROOT = Path(__file__).resolve().parents[1]
V3_DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


def _payload() -> dict:
    return {
        "schema": "podium7.catalog-identity-golden.v1",
        "datasetVersion": "operational-provenance-test-1",
        "createdAt": "2026-08-26",
        "sources": [
            {"id": "source-a", "publisher": "A", "url": "https://example.com/a"},
            {"id": "source-b", "publisher": "B", "url": "https://example.com/b"},
        ],
        "cases": [
            {
                "id": "case-1",
                "expected": "NO_MATCH",
                "left": {"make": "Example", "model": "One", "generation": "A"},
                "right": {"make": "Example", "model": "One", "generation": "B"},
                "sourceIds": ["source-b", "source-a"],
                "fieldSourceIds": {
                    "left": {
                        "make": ["source-a"],
                        "model": ["source-a"],
                        "generation": ["source-a"],
                    },
                    "right": {
                        "make": ["source-b"],
                        "model": ["source-b"],
                        "generation": ["source-b"],
                    },
                },
                "rationale": "synthetic provenance contract fixture",
            }
        ],
    }


def _write(payload: dict) -> Path:
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
    with handle:
        json.dump(payload, handle)
    return Path(handle.name)


class CatalogOperationalFieldProvenanceTests(unittest.TestCase):
    def test_replay_uses_explicit_field_attribution_not_source_list_position(self) -> None:
        path = _write(_payload())
        self.addCleanup(path.unlink, missing_ok=True)
        records = build_source_backed_operational_records((path,))
        self.assertEqual(2, len(records))
        self.assertEqual("source-a", records[0]["source"]["id"])
        self.assertEqual("source-b", records[1]["source"]["id"])

    def test_single_case_source_is_unambiguous_without_field_attribution(self) -> None:
        payload = _payload()
        payload["cases"][0]["sourceIds"] = ["source-a"]
        del payload["cases"][0]["fieldSourceIds"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        records = build_source_backed_operational_records((path,))
        self.assertEqual(2, len(records))
        self.assertEqual(["source-a", "source-a"], [record["source"]["id"] for record in records])

    def test_eligibility_measurement_separates_safe_records_without_replaying_blocked_ones(self) -> None:
        payload = _payload()
        explicit_case = payload["cases"][0]
        single_case = {
            "id": "single-source",
            "expected": "MATCH",
            "left": {"make": "Example", "model": "Solo"},
            "right": {"make": "Example", "model": "Solo"},
            "sourceIds": ["source-a"],
            "rationale": "sole source has no source-selection ambiguity",
        }
        blocked_case = {
            "id": "blocked-multisource",
            "expected": "REVIEW",
            "left": {"make": "Example", "model": "Blocked"},
            "right": {"make": "Example", "model": "Blocked"},
            "sourceIds": ["source-a", "source-b"],
            "rationale": "multiple sources without field attribution remain blocked",
        }
        payload["cases"] = [explicit_case, single_case, blocked_case]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)

        report = measure_operational_provenance_eligibility((path,))
        summary = report["summary"]
        self.assertEqual(3, summary["cases"])
        self.assertEqual(6, summary["records"])
        self.assertEqual(4, summary["replayableRecords"])
        self.assertEqual(2, summary["blockedRecords"])
        self.assertEqual(
            {"EXPLICIT_FIELD_ATTRIBUTION": 2, "SOLE_CASE_SOURCE": 2},
            summary["replayableByMethod"],
        )
        blocked = [item for item in report["records"] if not item["replayable"]]
        self.assertEqual({"blocked-multisource"}, {item["caseId"] for item in blocked})
        self.assertTrue(all("multiple sourceIds" in item["reason"] for item in blocked))

    def test_retained_v3_has_only_six_sole_source_cases_before_provenance_reconstruction(self) -> None:
        report = measure_operational_provenance_eligibility(V3_DATASETS)
        summary = report["summary"]
        self.assertEqual(36, summary["cases"])
        self.assertEqual(72, summary["records"])
        self.assertEqual(12, summary["replayableRecords"])
        self.assertEqual(60, summary["blockedRecords"])
        self.assertEqual(12 / 72, summary["replayableRate"])
        self.assertEqual({"SOLE_CASE_SOURCE": 12}, summary["replayableByMethod"])
        self.assertEqual({}, summary.get("explicitFieldAttributionBySource", {}))
        self.assertTrue(
            all(
                item["method"] == "SOLE_CASE_SOURCE"
                for item in report["records"]
                if item["replayable"]
            )
        )
        self.assertTrue(
            all(
                "multiple sourceIds" in item["reason"]
                for item in report["records"]
                if not item["replayable"]
            )
        )

    def test_multisource_case_without_field_attribution_is_skipped(self) -> None:
        payload = _payload()
        del payload["cases"][0]["fieldSourceIds"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, "operational corpus requires at least one record"):
            build_source_backed_operational_records((path,))

    def test_missing_field_attribution_fails_closed(self) -> None:
        payload = _payload()
        del payload["cases"][0]["fieldSourceIds"]["left"]["generation"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, "lacks explicit source attribution"):
            build_source_backed_operational_records((path,))

    def test_duplicate_field_source_ids_fail_closed(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["make"] = ["source-a", "source-a"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, "source ids must be unique|contains duplicates"):
            build_source_backed_operational_records((path,))

    def test_no_single_source_covering_full_record_fails_closed(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["generation"] = ["source-b"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, "no unique source common"):
            build_source_backed_operational_records((path,))

    def test_multiple_fully_covering_sources_remain_ambiguous(self) -> None:
        payload = _payload()
        for field_name in ("make", "model", "generation"):
            payload["cases"][0]["fieldSourceIds"]["left"][field_name] = ["source-a", "source-b"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, "no unique source common"):
            build_source_backed_operational_records((path,))


if __name__ == "__main__":
    unittest.main()
