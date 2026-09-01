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
GENERATION_SOURCE = "chevrolet-onix-second-generation"
MY26_PRICE_SOURCE = "chevrolet-onix-my26-price-list"
MY26_ENGINEERING_SOURCE = "chevrolet-onix-line-2026-engineering"
CASE_ID = "br-hard-review-onix-my26-premier-incomplete-mechanical-mapping"
PROBE_KEYS = (
    ("br-adjacent-incomplete-1.0", CASE_ID, "left"),
    ("br-adjacent-incomplete-1.0", CASE_ID, "right"),
)


def _mapping(side: str, field_sources: dict[str, list[str]]) -> dict:
    return {
        "benchmark": "catalog_identity_br_adjacent_incomplete_v1.json",
        "benchmarkDatasetVersion": "br-adjacent-incomplete-1.0",
        "caseId": CASE_ID,
        "side": side,
        "fieldSourceIds": field_sources,
        "evidenceBasis": {
            GENERATION_SOURCE: "Retained Chevrolet product-history evidence establishes the current Onix as the second generation.",
            MY26_PRICE_SOURCE: "Retained Chevrolet MY26 price list establishes Onix Premier 1.0 Turbo hatch, model year 2026 and six-speed automatic transmission.",
            MY26_ENGINEERING_SOURCE: "Retained Chevrolet engineering article establishes the 2026 Onix line, hatch body and Premier configuration while intentionally not mapping Premier mechanical fields.",
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


PROBE_MAPPINGS = (
    _mapping(
        "left",
        {
            "make": [MY26_PRICE_SOURCE],
            "model": [MY26_PRICE_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [MY26_PRICE_SOURCE],
            "powertrain": [MY26_PRICE_SOURCE],
            "transmission": [MY26_PRICE_SOURCE],
            "body_style": [MY26_PRICE_SOURCE],
            "market": [MY26_PRICE_SOURCE],
            "model_year_from": [MY26_PRICE_SOURCE],
            "model_year_to": [MY26_PRICE_SOURCE],
        },
    ),
    _mapping(
        "right",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [MY26_ENGINEERING_SOURCE],
            "body_style": [MY26_ENGINEERING_SOURCE],
            "market": [MY26_ENGINEERING_SOURCE],
            "model_year_from": [MY26_ENGINEERING_SOURCE],
            "model_year_to": [MY26_ENGINEERING_SOURCE],
        },
    ),
)


def _probe_records() -> list[dict]:
    payload = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-adjacent-onix-1",
        "createdAt": "2026-09-01",
        "mappings": list(PROBE_MAPPINGS),
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return build_multisource_operational_records(ACTIVE_PATHS, path)


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class AdjacentOnixMultisourceProbeTests(unittest.TestCase):
    def test_probe_builds_exact_two_field_complete_records(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 2)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        self.assertTrue(all(len(record["sourceIds"]) >= 2 for record in records))

    def test_probe_replays_after_retained_corpus_without_collapsing_missing_mechanics(self) -> None:
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

        actions = tuple(getattr(result.action, "value", str(result.action)) for result in results)
        published = len(store.catalog_vehicle_ids_page(after_id=None, limit=100))
        print(f"ADJACENT_ONIX_PROBE_ACTIONS={actions}", flush=True)
        print(f"ADJACENT_ONIX_PROBE_PUBLISHED={published}", flush=True)

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
