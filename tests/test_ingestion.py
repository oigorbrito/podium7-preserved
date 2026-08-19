from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from podium7.ingestion import SOURCE_ID, _stable_id, ingest_vehicle_makes_models_json
from podium7.persistence import EvidenceStore


SOURCE_PATH = Path("data/raw/vehicle-makes-models/artega.json")
ACQUIRED_AT = datetime(2026, 8, 19, tzinfo=timezone.utc)
GT_POINTER = "/makes/0/models/0/generations/0/engines/0"
GT_LOCATOR = (
    "https://github.com/gor3a/vehicle-makes-models/blob/main/"
    f"data/json/{SOURCE_PATH.name}#{GT_POINTER}"
)
GT_ENTITY_ID = _stable_id("entity", GT_LOCATOR)


class IngestionTests(unittest.TestCase):
    def test_real_snapshot_report_counts(self):
        with EvidenceStore() as store:
            report = ingest_vehicle_makes_models_json(store, SOURCE_PATH, acquired_at=ACQUIRED_AT)
        self.assertEqual(report.source_id, SOURCE_ID)
        self.assertEqual(report.makes, 1)
        self.assertEqual(report.models, 2)
        self.assertEqual(report.generations, 2)
        self.assertEqual(report.automotive_entities, 2)
        self.assertEqual(report.raw_evidence, 2)
        self.assertEqual(report.candidate_facts, 26)
        self.assertEqual(report.real_automotive_records, 2)

    def test_real_snapshot_persists_expected_counts(self):
        with EvidenceStore() as store:
            ingest_vehicle_makes_models_json(store, SOURCE_PATH, acquired_at=ACQUIRED_AT)
            counts = store.snapshot_counts()
        self.assertEqual(counts["sources"], 1)
        self.assertEqual(counts["automotive_entities"], 2)
        self.assertEqual(counts["raw_evidence"], 2)
        self.assertEqual(counts["candidate_facts"], 26)

    def test_raw_evidence_preserves_source_locator_and_snapshot_reference(self):
        with EvidenceStore() as store:
            ingest_vehicle_makes_models_json(store, SOURCE_PATH, acquired_at=ACQUIRED_AT)
            evidence = store.evidence_for_source(SOURCE_ID)
        self.assertEqual(len(evidence), 2)
        self.assertTrue(all(item.source_id == SOURCE_ID for item in evidence))
        self.assertTrue(all(item.raw_content_ref == str(SOURCE_PATH) for item in evidence))
        self.assertTrue(all(item.locator.startswith("https://github.com/gor3a/vehicle-makes-models/") for item in evidence))

    def test_gt_power_preserves_raw_and_normalizes_to_kw(self):
        with EvidenceStore() as store:
            ingest_vehicle_makes_models_json(store, SOURCE_PATH, acquired_at=ACQUIRED_AT)
            facts = {fact.attribute: fact for fact in store.candidates_for_entity(GT_ENTITY_ID)}
        self.assertEqual(facts["power"].raw_value, 300)
        self.assertEqual(facts["power"].normalized_value, 223.709961)
        self.assertEqual(facts["power"].unit, "kW")
        self.assertEqual(facts["power"].normalization_rule, "power.hp_to_kw.v1")
        self.assertEqual(facts["fuel_type"].raw_value, "Gasoline")
        self.assertEqual(facts["fuel_type"].normalized_value, "gasoline")

    def test_same_snapshot_produces_deterministic_candidate_ids(self):
        with EvidenceStore() as first:
            ingest_vehicle_makes_models_json(first, SOURCE_PATH, acquired_at=ACQUIRED_AT)
            first_ids = [fact.id for fact in first.candidates_for_entity(GT_ENTITY_ID)]
        with EvidenceStore() as second:
            ingest_vehicle_makes_models_json(second, SOURCE_PATH, acquired_at=ACQUIRED_AT)
            second_ids = [fact.id for fact in second.candidates_for_entity(GT_ENTITY_ID)]
        self.assertEqual(first_ids, second_ids)

    def test_reingestion_into_same_store_is_rejected(self):
        with EvidenceStore() as store:
            ingest_vehicle_makes_models_json(store, SOURCE_PATH, acquired_at=ACQUIRED_AT)
            with self.assertRaises(ValueError):
                ingest_vehicle_makes_models_json(store, SOURCE_PATH, acquired_at=ACQUIRED_AT)

    def test_failed_ingestion_rolls_back_partial_snapshot(self):
        payload = {
            "makes": [
                {
                    "name": "Atomic",
                    "models": [
                        {
                            "name": "Good",
                            "yearStart": 2020,
                            "yearEnd": 2021,
                            "generations": [
                                {
                                    "name": "Good (2020)",
                                    "yearStart": 2020,
                                    "yearEnd": 2021,
                                    "engines": [{"label": "1.0", "powerHp": 100}],
                                }
                            ],
                        },
                        {
                            "name": "Broken",
                            "yearStart": 2025,
                            "yearEnd": 2024,
                            "generations": [
                                {
                                    "name": "Broken (2025)",
                                    "yearStart": 2025,
                                    "yearEnd": 2024,
                                    "engines": [{"label": "1.0", "powerHp": 100}],
                                }
                            ],
                        },
                    ],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "malformed.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with EvidenceStore() as store:
                with self.assertRaises(ValueError):
                    ingest_vehicle_makes_models_json(store, path, acquired_at=ACQUIRED_AT)
                self.assertTrue(all(count == 0 for count in store.snapshot_counts().values()))


if __name__ == "__main__":
    unittest.main()
