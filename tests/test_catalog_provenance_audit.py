from pathlib import Path
import unittest

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_operational import run_source_backed_operational_corpus
from podium7.catalog_provenance_audit import audit_catalog_provenance


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


class CatalogProvenanceAuditTests(unittest.TestCase):
    def test_v3_replay_has_complete_persisted_provenance(self) -> None:
        store = CatalogStore()
        try:
            report = run_source_backed_operational_corpus(store, DATASETS)
            self.assertEqual(72, report.total)
            audit = audit_catalog_provenance(store)
            self.assertTrue(audit["summary"]["pass"])
            self.assertEqual(0, audit["summary"]["incompleteLinks"])
            self.assertEqual(1.0, audit["summary"]["completeness"])
        finally:
            store.close()

    def test_missing_persisted_evidence_is_detected(self) -> None:
        store = CatalogStore()
        try:
            run_source_backed_operational_corpus(store, DATASETS[:1])
            vehicle_id = store.catalog_vehicle_ids_page(limit=1)[0]
            candidate = store.catalog_candidates_for_entity(vehicle_id)[0]
            store._connection.execute("PRAGMA foreign_keys = OFF")
            store._connection.execute("DELETE FROM raw_evidence WHERE id = ?", (candidate.evidence_id,))
            store._connection.commit()
            audit = audit_catalog_provenance(store)
            self.assertFalse(audit["summary"]["pass"])
            self.assertIn("CANDIDATE_MISSING_EVIDENCE", {item["kind"] for item in audit["incomplete"]})
        finally:
            store.close()

    def test_audit_does_not_truncate_catalog_after_first_hundred_vehicles(self) -> None:
        store = CatalogStore()
        try:
            for index in range(101):
                store.create_catalog_vehicle(
                    CatalogVehicleIdentity(make="Test", model=f"Model {index:03d}")
                )
            audit = audit_catalog_provenance(store)
            self.assertEqual(101, audit["summary"]["catalogVehicles"])
            self.assertEqual(101, audit["summary"]["incompleteLinks"])
            self.assertEqual(
                101,
                sum(
                    item["kind"] == "CANONICAL_WITHOUT_CANDIDATE"
                    for item in audit["incomplete"]
                ),
            )
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
