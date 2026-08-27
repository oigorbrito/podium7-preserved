from pathlib import Path
import tempfile
import unittest

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from podium7.catalog_batch_failure import CatalogBatchFailureSnapshot, CatalogBatchFailureStore


def _record(*, evidence_id: str, generation: object | None = None) -> dict[str, object]:
    vehicle: dict[str, object] = {"make": "Toyota", "model": "Corolla"}
    if generation is not None:
        vehicle["generation"] = generation
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
        "vehicle": vehicle,
    }


class CatalogBatchFailureRetentionTests(unittest.TestCase):
    def test_failure_survives_database_reopen_and_success_does_not_create_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "catalog.sqlite")
            store = CatalogStore(database)
            envelopes = parse_catalog_batch_payload(
                {
                    "records": [
                        _record(evidence_id="evidence:ok"),
                        _record(evidence_id="evidence:bad", generation=17),
                    ]
                }
            )
            report = ingest_catalog_batch(store, envelopes)
            self.assertEqual(report.failed, 1)
            self.assertIsNone(CatalogBatchFailureStore(store).get("evidence:ok"))
            self.assertIsNone(store.get_raw_evidence("evidence:bad"))
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
            reopened.close()

    def test_repeated_identical_failure_is_idempotent(self) -> None:
        store = CatalogStore()
        try:
            envelopes = parse_catalog_batch_payload(
                {"records": [_record(evidence_id="evidence:bad", generation=17)]}
            )
            first = ingest_catalog_batch(store, envelopes)
            second = ingest_catalog_batch(store, envelopes)
            self.assertEqual(first.failed, 1)
            self.assertEqual(second.failed, 1)
            self.assertEqual(CatalogBatchFailureStore(store).count(), 1)
        finally:
            store.close()

    def test_same_evidence_id_with_different_failure_metadata_is_rejected(self) -> None:
        store = CatalogStore()
        try:
            first = parse_catalog_batch_payload(
                {"records": [_record(evidence_id="evidence:bad", generation=17)]}
            )
            ingest_catalog_batch(store, first)
            changed = _record(evidence_id="evidence:bad", generation=19)
            changed["recordId"] = "changed-record"
            second = parse_catalog_batch_payload({"records": [changed]})
            with self.assertRaisesRegex(ValueError, "already exists with different metadata"):
                ingest_catalog_batch(store, second)
        finally:
            store.close()

    def test_malformed_failure_snapshot_fails_closed(self) -> None:
        valid = {
            "evidence_id": "evidence:bad",
            "index": 0,
            "record_id": "record:evidence:bad",
            "source_id": "source:test",
            "source_locator": "https://example.test/source",
            "evidence_locator": "https://example.test/evidence",
            "raw_content_ref": "test:evidence:bad",
            "error_code": "CATALOG_BATCH_RECORD_INVALID",
            "error_message": "invalid vehicle",
        }
        for field, value in (("index", -1), ("index", False), ("evidence_id", ""), ("error_message", " ")):
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    CatalogBatchFailureSnapshot(**{**valid, field: value})

    def test_store_rejects_corrupted_persisted_payloads(self) -> None:
        store = CatalogStore()
        try:
            failure_store = CatalogBatchFailureStore(store)
            corruptions = (
                ("bad-json", "not-json", "valid JSON"),
                ("array", "[]", "JSON object"),
                ("bad-error", '{"evidenceId":"e","index":0,"recordId":null,"sourceId":"s","sourceLocator":"l","evidenceLocator":"l","rawContentRef":"r","error":"bad"}', "error must be a JSON object"),
                ("missing-field", '{"index":0,"recordId":null,"sourceId":"s","sourceLocator":"l","evidenceLocator":"l","rawContentRef":"r","error":{"code":"c","message":"m"}}', "missing field evidenceId"),
            )
            for evidence_id, payload, pattern in corruptions:
                with self.subTest(evidence_id=evidence_id):
                    store._connection.execute(
                        "INSERT INTO catalog_batch_failures(evidence_id, payload_json) VALUES (?, ?)",
                        (evidence_id, payload),
                    )
                    store._connection.commit()
                    with self.assertRaisesRegex(ValueError, pattern):
                        failure_store.get(evidence_id)
        finally:
            store.close()

    def test_store_initialization_does_not_commit_outer_transaction(self) -> None:
        store = CatalogStore()
        try:
            vehicle_id = None
            with self.assertRaisesRegex(RuntimeError, "rollback marker"):
                with store.transaction():
                    vehicle_id = store.create_catalog_vehicle(
                        CatalogVehicleIdentity(make="Test", model="Transactional")
                    )
                    CatalogBatchFailureStore(store)
                    raise RuntimeError("rollback marker")
            self.assertIsNotNone(vehicle_id)
            self.assertIsNone(store.get_catalog_vehicle(vehicle_id))
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
