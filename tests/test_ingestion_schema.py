import json
from pathlib import Path
import tempfile
import unittest

from podium7.ingestion import ingest_vehicle_makes_models_json
from podium7.persistence import EvidenceStore


class StructuredIngestionSchemaTests(unittest.TestCase):
    def _write(self, directory: str, payload: object) -> Path:
        path = Path(directory) / "snapshot.json"
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _assert_rejected_without_writes(self, path: Path) -> None:
        with EvidenceStore() as store:
            with self.assertRaises(ValueError):
                ingest_vehicle_makes_models_json(store, path)
            self.assertTrue(all(count == 0 for count in store.snapshot_counts().values()))

    def _valid_payload(self) -> dict:
        return {
            "makes": [
                {
                    "name": "Example",
                    "models": [
                        {
                            "name": "Model",
                            "generations": [
                                {
                                    "name": "Generation",
                                    "engines": [{"label": "1.0"}],
                                }
                            ],
                        }
                    ],
                }
            ]
        }

    def test_missing_required_structural_key_rejected_without_writes(self):
        payload = self._valid_payload()
        del payload["makes"][0]["models"]
        with tempfile.TemporaryDirectory() as directory:
            self._assert_rejected_without_writes(self._write(directory, payload))

    def test_wrong_structural_collection_type_rejected_without_writes(self):
        payload = self._valid_payload()
        payload["makes"][0]["models"][0]["generations"][0]["engines"] = {}
        with tempfile.TemporaryDirectory() as directory:
            self._assert_rejected_without_writes(self._write(directory, payload))

    def test_engine_requires_non_empty_label(self):
        for engine in ({}, {"label": ""}):
            payload = self._valid_payload()
            payload["makes"][0]["models"][0]["generations"][0]["engines"] = [engine]
            with self.subTest(engine=engine), tempfile.TemporaryDirectory() as directory:
                self._assert_rejected_without_writes(self._write(directory, payload))

    def test_snapshot_requires_at_least_one_engine_record(self):
        payload = self._valid_payload()
        payload["makes"][0]["models"][0]["generations"][0]["engines"] = []
        with tempfile.TemporaryDirectory() as directory:
            self._assert_rejected_without_writes(self._write(directory, payload))

    def test_non_standard_json_constant_rejected_before_writes(self):
        payload = (
            '{"makes":[{"name":"Example","models":[{"name":"Model",'
            '"generations":[{"name":"Generation","engines":[{"label":"1.0",'
            '"powerHp":NaN}]}]}]}]}'
        )
        with tempfile.TemporaryDirectory() as directory:
            self._assert_rejected_without_writes(self._write(directory, payload))


if __name__ == "__main__":
    unittest.main()
