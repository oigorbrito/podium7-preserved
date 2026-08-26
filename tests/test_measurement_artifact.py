from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from podium7.measurement_artifact import (
    MEASUREMENT_ARTIFACT_SCHEMA,
    build_measurement_artifact,
    measurement_artifact_json,
    write_measurement_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


class MeasurementArtifactTests(unittest.TestCase):
    def test_v3_artifact_binds_exact_dataset_bytes_deterministically(self) -> None:
        first = measurement_artifact_json(DATASETS)
        second = measurement_artifact_json(DATASETS)
        self.assertEqual(first, second)
        artifact = json.loads(first)
        self.assertEqual(artifact["schema"], MEASUREMENT_ARTIFACT_SCHEMA)
        self.assertEqual(len(artifact["datasets"]), 4)
        self.assertEqual(artifact["identityQuality"]["totalCases"], 36)
        self.assertEqual(artifact["operational"]["summary"]["total"], 72)
        for descriptor, path in zip(artifact["datasets"], DATASETS, strict=True):
            raw = path.read_bytes()
            self.assertEqual(descriptor["name"], path.name)
            self.assertEqual(descriptor["sha256"], sha256(raw).hexdigest())
            self.assertEqual(descriptor["bytes"], len(raw))
            declared = json.loads(raw.decode("utf-8"))["datasetVersion"]
            self.assertEqual(descriptor["datasetVersion"], declared)

    def test_writer_is_byte_for_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            write_measurement_artifact(first, DATASETS)
            write_measurement_artifact(second, DATASETS)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_missing_dataset_version_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(json.dumps({"schema": "podium7.catalog-identity-golden.v1", "cases": []}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "datasetVersion is required"):
                build_measurement_artifact((path,))


if __name__ == "__main__":
    unittest.main()
