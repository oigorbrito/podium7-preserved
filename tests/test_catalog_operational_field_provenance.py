import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog_operational import build_source_backed_operational_records


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

    def test_multisource_case_without_field_attribution_fails_closed(self) -> None:
        payload = _payload()
        del payload["cases"][0]["fieldSourceIds"]
        path = _write(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, "multiple sourceIds"):
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
        with self.assertRaisesRegex(ValueError, "contains duplicates"):
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
