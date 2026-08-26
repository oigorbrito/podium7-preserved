from pathlib import Path
import tempfile
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from podium7.catalog_batch_failure import CatalogBatchFailureStore


def _record(*, evidence_id: str, make: object = "Toyota") -> dict[str, object]:
    return {
        "recordId": f"record:{evidence_id}",
        "source": {
            "id": "source:test",
            "name": "Test source",
            "locator": "https://example.test/source",
        },
        "evidence": {
            "id": evidence_id,
            "locator": "https://example.test/evidence",
            "retrievedAt": "2026-08-26T00:00:00Z",
            "acquisitionMethod": "test",
            "rawContentRef": f"test:{evidence_id}",
        },
        "vehicle": {"make": make, "model": "Corolla"},
    }


class CatalogBatchFailureRetentionTests(unittest.TestCase):
    def test_failure_survives_database_reopen_and_success_does_not_create_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "catalog.sqlite")
            store = CatalogStore(database)
            envelopes = parse_catalog_batch_payload(
                {"records": [_record(evidence_id="evidence:ok"), _record(evidence_id="evidence:bad", make=17)]}
            )
            report = ingest_catalog_batch(store, envelopes)
            self.assertEqual(report.failed, 1)
            self.assertIsNone(CatalogBatchFailureStore(store).get("evidence:ok"))
            failed = CatalogBatchFailureStore(store).get("evidence:bad")
            self.assertIsNotNone(failed)
            self.assertEqual(failed.record_id, "record:evidence:bad")
            self.assertEqual(failed.source_id, "source:test")
            self.assertEqual(failed.error_code, "CATALOG_BATCH_RECORD_INVALID")
            store._connection.close()

            reopened = CatalogStore(database)
            retained = CatalogBatchFailureStore(reopened).get("evidence:bad")
            self.assertIsNotNone(retained)
            self.assertEqual(retained.raw_content_ref, "test:evidence:bad")
            self.assertEqual(CatalogBatchFailureStore(reopened).count(), 1)

    def test_repeated_identical_failure_is_idempotent(self) -> None:
        store = CatalogStore()
        envelopes = parse_catalog_batch_payload({"records": [_record(evidence_id="evidence:bad", make=17)]})
        first = ingest_catalog_batch(store, envelopes)
        second = ingest_catalog_batch(store, envelopes)
        self.assertEqual(first.failed, 1)
        self.assertEqual(second.failed, 1)
        self.assertEqual(CatalogBatchFailureStore(store).count(), 1)

    def test_same_evidence_id_with_different_failure_metadata_is_rejected(self) -> None:
        store = CatalogStore()
        first = parse_catalog_batch_payload({"records": [_record(evidence_id="evidence:bad", make=17)]})
        ingest_catalog_batch(store, first)
        changed = _record(evidence_id="evidence:bad", make=19)
        changed["recordId"] = "changed-record"
        second = parse_catalog_batch_payload({"records": [changed]})
        with self.assertRaisesRegex(ValueError, "already exists with different metadata"):
            ingest_catalog_batch(store, second)


if __name__ == "__main__":
    unittest.main()
