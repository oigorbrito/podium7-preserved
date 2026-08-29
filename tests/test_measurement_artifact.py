from hashlib import sha256
import json
import math
from pathlib import Path
import tempfile
import unittest

from podium7.measurement_artifact import (
    MEASUREMENT_ARTIFACT_SCHEMA,
    MEASUREMENT_CONTRACT_VERSION,
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


def dataset_versions(paths=DATASETS):
    return [json.loads(path.read_text(encoding="utf-8"))["datasetVersion"] for path in paths]


def identity_report(paths=DATASETS):
    return {
        "schema": "podium7.production-identity-quality.v1",
        "datasets": dataset_versions(paths),
        "totalCases": 1,
        "metrics": {
            "autoMatchPrecision": 1.0,
            "autoMatchRecall": 1.0,
            "falseMergeCount": 0,
            "missedMatchCount": 0,
            "ambiguousOvercommitCount": 0,
            "reviewRate": 0.0,
        },
        "cases": [],
    }


def operational_report():
    return {
        "schema": "podium7.production-operational-measurement.v1",
        "summary": {"total": 1, "created": 1, "matched": 0, "review": 0, "failed": 0},
    }


class MeasurementArtifactTests(unittest.TestCase):
    def test_artifact_binds_exact_dataset_bytes_and_supplied_reports_deterministically(self) -> None:
        identity = identity_report()
        operational = operational_report()
        first = measurement_artifact_json(
            DATASETS,
            identity_quality=identity,
            operational=operational,
        )
        second = measurement_artifact_json(
            DATASETS,
            identity_quality=identity,
            operational=operational,
        )
        self.assertEqual(first, second)
        artifact = json.loads(first)
        self.assertEqual(artifact["schema"], MEASUREMENT_ARTIFACT_SCHEMA)
        self.assertEqual(artifact["measurementContractVersion"], MEASUREMENT_CONTRACT_VERSION)
        self.assertEqual(artifact["identityQuality"], identity)
        self.assertEqual(artifact["operational"], operational)
        self.assertEqual(len(artifact["datasets"]), 4)
        for descriptor, path in zip(artifact["datasets"], DATASETS, strict=True):
            raw = path.read_bytes()
            self.assertEqual(descriptor["name"], path.name)
            self.assertEqual(descriptor["sha256"], sha256(raw).hexdigest())
            self.assertEqual(descriptor["bytes"], len(raw))
            declared = json.loads(raw.decode("utf-8"))["datasetVersion"]
            self.assertEqual(descriptor["datasetVersion"], declared)

    def test_writer_is_byte_for_byte_reproducible(self) -> None:
        identity = identity_report()
        operational = operational_report()
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.json"
            second = Path(directory) / "second.json"
            write_measurement_artifact(
                first,
                DATASETS,
                identity_quality=identity,
                operational=operational,
            )
            write_measurement_artifact(
                second,
                DATASETS,
                identity_quality=identity,
                operational=operational,
            )
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_missing_dataset_version_and_non_object_dataset_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"
            missing.write_text(json.dumps({"schema": "podium7.catalog-identity-golden.v1", "cases": []}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "datasetVersion is required"):
                build_measurement_artifact(
                    (missing,),
                    identity_quality={**identity_report(), "datasets": ["missing"]},
                    operational=operational_report(),
                )

            array = Path(directory) / "array.json"
            array.write_text(json.dumps([{"datasetVersion": "x"}]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON object"):
                build_measurement_artifact(
                    (array,),
                    identity_quality={**identity_report(), "datasets": ["x"]},
                    operational=operational_report(),
                )

    def test_duplicate_dataset_input_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "dataset inputs must be unique"):
            build_measurement_artifact(
                (DATASETS[0], DATASETS[0]),
                identity_quality=identity_report((DATASETS[0], DATASETS[0])),
                operational=operational_report(),
            )

    def test_duplicate_dataset_name_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first_dir = Path(directory) / "a"
            second_dir = Path(directory) / "b"
            first_dir.mkdir()
            second_dir.mkdir()
            first = first_dir / "same.json"
            second = second_dir / "same.json"
            first.write_bytes(DATASETS[0].read_bytes())
            second.write_bytes(DATASETS[1].read_bytes())
            with self.assertRaisesRegex(ValueError, "dataset names must be unique"):
                build_measurement_artifact(
                    (first, second),
                    identity_quality={
                        **identity_report(),
                        "datasets": dataset_versions((first, second)),
                    },
                    operational=operational_report(),
                )

    def test_identity_report_must_match_input_dataset_versions(self) -> None:
        with self.assertRaisesRegex(ValueError, "dataset versions do not match"):
            build_measurement_artifact(
                DATASETS,
                identity_quality={**identity_report(), "datasets": ["wrong"]},
                operational=operational_report(),
            )

    def test_report_schemas_and_strict_json_are_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "identity quality report schema"):
            build_measurement_artifact(
                DATASETS,
                identity_quality={**identity_report(), "schema": "wrong"},
                operational=operational_report(),
            )
        with self.assertRaisesRegex(ValueError, "operational measurement report schema"):
            build_measurement_artifact(
                DATASETS,
                identity_quality=identity_report(),
                operational={**operational_report(), "schema": "wrong"},
            )
        with self.assertRaisesRegex(ValueError, "strict JSON-compatible"):
            build_measurement_artifact(
                DATASETS,
                identity_quality={**identity_report(), "nonFinite": math.nan},
                operational=operational_report(),
            )


if __name__ == "__main__":
    unittest.main()
