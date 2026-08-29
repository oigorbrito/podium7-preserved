import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_operational import (
    build_source_backed_operational_records,
    run_source_backed_operational_corpus,
)


class OperationalSourceAttributionTests(unittest.TestCase):
    def _write_fixture(self, payload: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "fixture.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _base_payload(self) -> dict:
        return {
            "schema": "podium7.catalog-identity-golden.v1",
            "datasetVersion": "source-attribution-v1",
            "createdAt": "2026-08-29",
            "sources": [
                {"id": "source-a", "publisher": "A", "url": "https://example.test/a"},
                {"id": "source-b", "publisher": "B", "url": "https://example.test/b"},
            ],
            "cases": [
                {
                    "id": "case-1",
                    "expected": "MATCH",
                    "left": {"make": "Toyota", "model": "Corolla"},
                    "right": {"make": "Toyota", "model": "Corolla"},
                    "sourceIds": ["source-a"],
                }
            ],
        }

    def test_multi_source_case_fails_closed(self) -> None:
        payload = self._base_payload()
        payload["cases"][0]["sourceIds"] = ["source-a", "source-b"]
        path = self._write_fixture(payload)
        with self.assertRaisesRegex(ValueError, "ambiguous case-level source attribution"):
            build_source_backed_operational_records((path,))

    def test_unknown_source_id_fails_closed(self) -> None:
        payload = self._base_payload()
        payload["cases"][0]["sourceIds"] = ["missing-source"]
        path = self._write_fixture(payload)
        with self.assertRaisesRegex(ValueError, "references unknown source"):
            build_source_backed_operational_records((path,))

    def test_single_source_replay_remains_supported(self) -> None:
        path = self._write_fixture(self._base_payload())
        records = build_source_backed_operational_records((path,))
        self.assertEqual(len(records), 2)
        self.assertEqual({record["source"]["id"] for record in records}, {"source-a"})
        store = CatalogStore()
        try:
            report = run_source_backed_operational_corpus(store, (path,))
            self.assertTrue(report.ok)
            self.assertEqual(report.total, 2)
            self.assertEqual(report.failed, 0)
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
