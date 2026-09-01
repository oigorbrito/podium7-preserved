import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.operational_multisource import (
    build_multisource_operational_records,
    run_multisource_operational_records,
)
from podium7.operational_provenance import run_provenance_eligible_operational_corpus


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATHS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
RETAINED_ATTRIBUTION_PATH = ROOT / "benchmarks" / "operational_multisource_field_attribution_v1.json"
TOYOTA_COROLLA_SOURCE = "toyota-corolla-2006-global"
TOYOTA_FUEL_SOURCE = "toyota-2zr-fe-gasoline-2006"
PORSCHE_GENERATION_SOURCE = "porsche-911-generations-2019"
PORSCHE_TECH_SOURCE = "porsche-911-carrera-s-991-tech-spec"
PROBE_KEYS = (
    ("1.0", "no-match-toyota-corolla-10g-vs-12g", "left"),
    ("1.0", "no-match-porsche-911-991-vs-992", "left"),
)


def _augmented_global_benchmark(directory: Path) -> Path:
    payload = json.loads(ACTIVE_PATHS[0].read_text(encoding="utf-8"))
    payload["sources"].extend(
        [
            {
                "id": TOYOTA_FUEL_SOURCE,
                "publisher": "Toyota Motor Corporation",
                "title": "Toyota Reinforces Efforts for Environmental Technologies and Environmentally Friendly Vehicles",
                "url": "https://global.toyota/en/detail/274024",
                "supports": "Toyota's 2006 2ZR-FE technical data explicitly identifies the 1,797 cc engine fuel type as regular unleaded gasoline.",
            },
            {
                "id": PORSCHE_TECH_SOURCE,
                "publisher": "Porsche",
                "title": "2013 911 Carrera (991) and 911 Carrera S (991) technical specifications",
                "url": "https://newsroom.porsche.com/dam/jcr:e1638451-d7dc-4f0e-a00d-b169cf342b86/2013_911_Technical_Specifications.pdf",
                "supports": "Official Porsche 991 Carrera S specifications identify the Carrera S, horizontally opposed six-cylinder engine and two-plus-two sport coupe body.",
            },
        ]
    )
    path = directory / "catalog_identity_golden_v1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _overlay(directory: Path) -> Path:
    payload = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-primary-evidence-closure-1",
        "createdAt": "2026-09-01",
        "mappings": [
            {
                "benchmark": "catalog_identity_golden_v1.json",
                "benchmarkDatasetVersion": "1.0",
                "caseId": "no-match-toyota-corolla-10g-vs-12g",
                "side": "left",
                "fieldSourceIds": {
                    "make": [TOYOTA_COROLLA_SOURCE],
                    "model": [TOYOTA_COROLLA_SOURCE],
                    "generation": [TOYOTA_COROLLA_SOURCE],
                    "powertrain": [TOYOTA_COROLLA_SOURCE, TOYOTA_FUEL_SOURCE],
                    "body_style": [TOYOTA_COROLLA_SOURCE],
                    "aliases": [TOYOTA_COROLLA_SOURCE],
                },
                "evidenceBasis": {
                    TOYOTA_COROLLA_SOURCE: "Retained Toyota launch evidence identifies the tenth-generation Corolla Axio sedan and its 1.8-liter 2ZR-FE engine.",
                    TOYOTA_FUEL_SOURCE: "Separate Toyota technical evidence explicitly identifies the 2ZR-FE fuel type as regular unleaded gasoline, closing the benchmark's petrol semantics without inference.",
                },
                "status": "PROBE_ONLY_NOT_RETAINED",
            },
            {
                "benchmark": "catalog_identity_golden_v1.json",
                "benchmarkDatasetVersion": "1.0",
                "caseId": "no-match-porsche-911-991-vs-992",
                "side": "left",
                "fieldSourceIds": {
                    "make": [PORSCHE_TECH_SOURCE],
                    "model": [PORSCHE_TECH_SOURCE],
                    "generation": [PORSCHE_GENERATION_SOURCE],
                    "variant": [PORSCHE_TECH_SOURCE],
                    "powertrain": [PORSCHE_TECH_SOURCE],
                    "body_style": [PORSCHE_TECH_SOURCE],
                },
                "evidenceBasis": {
                    PORSCHE_GENERATION_SOURCE: "Retained Porsche history explicitly identifies type 991 as the seventh-generation 911.",
                    PORSCHE_TECH_SOURCE: "Official Porsche Carrera S (991) specifications establish Carrera S, horizontally opposed six-cylinder powertrain and coupe body.",
                },
                "status": "PROBE_ONLY_NOT_RETAINED",
            },
        ],
    }
    path = directory / "probe.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _probe_records() -> list[dict]:
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        augmented_global = _augmented_global_benchmark(directory)
        overlay = _overlay(directory)
        paths = (augmented_global, ACTIVE_PATHS[1], ACTIVE_PATHS[2])
        return build_multisource_operational_records(paths, overlay)


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class PrimaryEvidenceClosureProbeTests(unittest.TestCase):
    def test_probe_builds_exact_two_previously_insufficient_sides(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 2)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        self.assertTrue(all(len(record["sourceIds"]) == 2 for record in records))

    def test_probe_replays_after_current_retained_corpus_with_exact_provenance(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)

        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)

        retained_records = build_multisource_operational_records(
            ACTIVE_PATHS,
            RETAINED_ATTRIBUTION_PATH,
        )
        self.assertEqual(len(retained_records), 16)
        run_multisource_operational_records(store, retained_records)

        records = _probe_records()
        results = run_multisource_operational_records(store, records)
        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.action in allowed for result in results))

        for record, result in zip(records, results):
            if result.action is CatalogIngestionAction.REVIEW:
                self.assertIsNotNone(result.review_id)
                continue
            self.assertIsNotNone(result.vehicle_id)
            expected_bindings = {
                (field_name, evidence_id)
                for field_name, evidence_ids in record["payload"]["provenance"]["fieldEvidence"].items()
                for evidence_id in evidence_ids
            }
            actual_bindings = {
                (fact.attribute, fact.evidence_id)
                for fact in store.catalog_candidates_for_entity(result.vehicle_id)
            }
            self.assertEqual(actual_bindings, expected_bindings)


if __name__ == "__main__":
    unittest.main()
