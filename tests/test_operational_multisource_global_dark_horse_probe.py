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


ACTIVE_PATHS = (
    "benchmarks/catalog_identity_golden_v1.json",
    "benchmarks/catalog_identity_golden_br_v1.json",
    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
)
RETAINED_ATTRIBUTION_PATH = "benchmarks/operational_multisource_field_attribution_v1.json"
SPEC_SOURCE = "ford-mustang-2024-eu-spec"
GENERATION_SOURCE = "ford-mustang-dark-horse-2022"
PROBE_KEYS = (
    ("1.0", "match-ford-mustang-dark-horse", "left"),
    ("1.0", "match-ford-mustang-dark-horse", "right"),
    ("1.0", "no-match-ford-mustang-gt-vs-dark-horse", "right"),
)


def _mapping(case_id: str, side: str) -> dict:
    return {
        "benchmark": "catalog_identity_golden_v1.json",
        "benchmarkDatasetVersion": "1.0",
        "caseId": case_id,
        "side": side,
        "fieldSourceIds": {
            "make": [SPEC_SOURCE],
            "model": [SPEC_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [SPEC_SOURCE],
            "powertrain": [SPEC_SOURCE],
            "body_style": [SPEC_SOURCE],
        },
        "evidenceBasis": {
            SPEC_SOURCE: "Retained Ford technical specification establishes Mustang Dark Horse, coupe body and 5.0 V8 configuration.",
            GENERATION_SOURCE: "Retained Ford Dark Horse material explicitly places Dark Horse in the seventh-generation 2024 Mustang family.",
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


PROBE_MAPPINGS = (
    _mapping("match-ford-mustang-dark-horse", "left"),
    _mapping("match-ford-mustang-dark-horse", "right"),
    _mapping("no-match-ford-mustang-gt-vs-dark-horse", "right"),
)


def _probe_records() -> list[dict]:
    payload = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-global-dark-horse-1",
        "createdAt": "2026-09-01",
        "mappings": list(PROBE_MAPPINGS),
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return build_multisource_operational_records(ACTIVE_PATHS, path)


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class GlobalDarkHorseMultisourceProbeTests(unittest.TestCase):
    def test_probe_builds_only_the_three_source_supported_sides(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 3)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        self.assertTrue(all(set(record["sourceIds"]) == {SPEC_SOURCE, GENERATION_SOURCE} for record in records))

    def test_probe_replays_after_retained_corpus_without_promoting_gt_generation(self) -> None:
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
        self.assertEqual(len(results), 3)
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
            self.assertTrue(expected_bindings <= actual_bindings)


if __name__ == "__main__":
    unittest.main()
