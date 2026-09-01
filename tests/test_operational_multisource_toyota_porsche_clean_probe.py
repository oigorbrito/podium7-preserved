from __future__ import annotations

from collections import Counter
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
from podium7.operational_multisource_overlay_set import (
    build_multisource_operational_records_from_overlays,
)
from podium7.operational_provenance import run_provenance_eligible_operational_corpus


ACTIVE_PATHS = (
    "benchmarks/catalog_identity_golden_v1.json",
    "benchmarks/catalog_identity_golden_br_v1.json",
    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
)
RETAINED_ATTRIBUTION_PATHS = (
    "benchmarks/operational_multisource_field_attribution_v1.json",
    "benchmarks/operational_multisource_field_attribution_tcross_adjacent_v1.json",
    "benchmarks/operational_multisource_field_attribution_onix_v1.json",
    "benchmarks/operational_multisource_field_attribution_mustang_v1.json",
)
TOYOTA_KEY = ("1.0", "no-match-toyota-corolla-10g-vs-12g", "left")
PORSCHE_KEY = ("1.0", "no-match-porsche-911-991-vs-992", "left")
TOYOTA_COROLLA_SOURCE = "toyota-corolla-2006-global"
TOYOTA_GASOLINE_SOURCE = "toyota-2zr-fe-gasoline-2006"
PORSCHE_GENERATION_SOURCE = "porsche-911-generations-2019"
PORSCHE_TECH_SPEC_SOURCE = "porsche-911-carrera-s-991-tech-spec"


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _common_field_source(field_source_ids: dict[str, list[str]]) -> set[str]:
    return set.intersection(*(set(source_ids) for source_ids in field_source_ids.values()))


def _augmented_global_benchmark(directory: Path) -> Path:
    source_path = Path("benchmarks/catalog_identity_golden_v1.json")
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    payload["sources"].extend(
        [
            {
                "id": TOYOTA_GASOLINE_SOURCE,
                "publisher": "Toyota Motor Corporation",
                "title": (
                    "Toyota Reinforces Efforts for Environmental Technologies "
                    "and Environmentally Friendly Vehicles"
                ),
                "url": "https://global.toyota/en/detail/274024",
                "supports": "2ZR-FE, 1,797 cc, regular unleaded gasoline.",
            },
            {
                "id": PORSCHE_TECH_SPEC_SOURCE,
                "publisher": "Porsche",
                "title": (
                    "2013 911 Carrera (991) and 911 Carrera S (991) "
                    "technical specifications"
                ),
                "url": (
                    "https://newsroom.porsche.com/dam/jcr:"
                    "e1638451-d7dc-4f0e-a00d-b169cf342b86/"
                    "2013_911_Technical_Specifications.pdf"
                ),
                "supports": (
                    "Porsche 911 Carrera S 991 horizontally opposed "
                    "six-cylinder coupe."
                ),
            },
        ]
    )
    for case in payload["cases"]:
        if case["id"] == "no-match-toyota-corolla-10g-vs-12g":
            case["sourceIds"].append(TOYOTA_GASOLINE_SOURCE)
        if case["id"] == "no-match-porsche-911-991-vs-992":
            case["sourceIds"].append(PORSCHE_TECH_SPEC_SOURCE)
    return _write_json(directory / "catalog_identity_golden_v1.json", payload)


def _toyota_porsche_overlay(directory: Path) -> Path:
    return _write_json(
        directory / "operational_multisource_field_attribution_toyota_porsche_probe.json",
        {
            "schema": "podium7.catalog-operational-field-attribution.v1",
            "datasetVersion": "toyota-porsche-clean-probe-1",
            "mappings": [
                {
                    "benchmark": "catalog_identity_golden_v1.json",
                    "benchmarkDatasetVersion": "1.0",
                    "caseId": "no-match-toyota-corolla-10g-vs-12g",
                    "side": "left",
                    "fieldSourceIds": {
                        "aliases": [TOYOTA_COROLLA_SOURCE],
                        "body_style": [TOYOTA_COROLLA_SOURCE],
                        "generation": [TOYOTA_COROLLA_SOURCE],
                        "make": [TOYOTA_COROLLA_SOURCE],
                        "model": [TOYOTA_COROLLA_SOURCE],
                        "powertrain": [TOYOTA_GASOLINE_SOURCE],
                    },
                },
                {
                    "benchmark": "catalog_identity_golden_v1.json",
                    "benchmarkDatasetVersion": "1.0",
                    "caseId": "no-match-porsche-911-991-vs-992",
                    "side": "left",
                    "fieldSourceIds": {
                        "body_style": [PORSCHE_TECH_SPEC_SOURCE],
                        "generation": [PORSCHE_GENERATION_SOURCE],
                        "make": [PORSCHE_TECH_SPEC_SOURCE],
                        "model": [PORSCHE_TECH_SPEC_SOURCE],
                        "powertrain": [PORSCHE_TECH_SPEC_SOURCE],
                        "variant": [PORSCHE_TECH_SPEC_SOURCE],
                    },
                },
            ],
        },
    )


class ToyotaPorscheCleanProbeTests(unittest.TestCase):
    def test_probe_builds_exact_two_records_after_current_retained_corpus(self) -> None:
        retained_records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            RETAINED_ATTRIBUTION_PATHS,
        )
        self.assertEqual(len(retained_records), 32)

        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            benchmark_path = _augmented_global_benchmark(directory)
            overlay_path = _toyota_porsche_overlay(directory)

            records = build_multisource_operational_records(
                (
                    benchmark_path,
                    "benchmarks/catalog_identity_golden_br_v1.json",
                    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
                ),
                overlay_path,
            )

        self.assertEqual([_key(record) for record in records], [TOYOTA_KEY, PORSCHE_KEY])
        self.assertEqual(
            records[0]["sourceIds"],
            tuple(sorted((TOYOTA_COROLLA_SOURCE, TOYOTA_GASOLINE_SOURCE))),
        )
        self.assertEqual(
            records[1]["sourceIds"],
            tuple(sorted((PORSCHE_GENERATION_SOURCE, PORSCHE_TECH_SPEC_SOURCE))),
        )
        toyota_field_sources = {
            field: [
                evidence_id.rsplit(":", 1)[1]
                for evidence_id in evidence_ids
            ]
            for field, evidence_ids in records[0]["payload"]["provenance"]["fieldEvidence"].items()
        }
        self.assertEqual(
            set().union(*(set(source_ids) for source_ids in toyota_field_sources.values())),
            {TOYOTA_COROLLA_SOURCE, TOYOTA_GASOLINE_SOURCE},
        )
        self.assertEqual(_common_field_source(toyota_field_sources), set())
        self.assertEqual(
            toyota_field_sources["powertrain"],
            [TOYOTA_GASOLINE_SOURCE],
        )
        self.assertNotIn(TOYOTA_COROLLA_SOURCE, toyota_field_sources["powertrain"])
        porsche_field_sources = {
            field: [
                evidence_id.rsplit(":", 1)[1]
                for evidence_id in evidence_ids
            ]
            for field, evidence_ids in records[1]["payload"]["provenance"]["fieldEvidence"].items()
        }
        self.assertEqual(_common_field_source(porsche_field_sources), set())
        self.assertEqual(porsche_field_sources["generation"], [PORSCHE_GENERATION_SOURCE])
        self.assertNotIn(
            PORSCHE_TECH_SPEC_SOURCE,
            porsche_field_sources["generation"],
        )

    def test_probe_replays_with_complete_field_provenance(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)

        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)

        retained_records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            RETAINED_ATTRIBUTION_PATHS,
        )
        retained_results = run_multisource_operational_records(store, retained_records)
        self.assertEqual(len(retained_results), 32)

        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            benchmark_path = _augmented_global_benchmark(directory)
            overlay_path = _toyota_porsche_overlay(directory)
            records = build_multisource_operational_records(
                (
                    benchmark_path,
                    "benchmarks/catalog_identity_golden_br_v1.json",
                    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
                ),
                overlay_path,
            )
            results = run_multisource_operational_records(store, records)

        self.assertEqual(len(results), 2)
        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertTrue(all(result.action in allowed for result in results))
        self.assertEqual(Counter(result.action for result in results), Counter({CatalogIngestionAction.CREATED: 2}))

        for record, result in zip(records, results):
            if result.action is CatalogIngestionAction.REVIEW:
                self.assertIsNotNone(result.review_id)
                self.assertIsNone(result.vehicle_id)
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
            self.assertTrue(expected_bindings <= actual_bindings)


if __name__ == "__main__":
    unittest.main()
