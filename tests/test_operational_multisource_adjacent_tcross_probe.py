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
GENERATION_SOURCE = "vw-tcross-brazil-generation"
LAUNCH_SOURCE = "vw-tcross-launch-versions"
TECH_SHEET_SOURCE = "vw-tcross-highline-250-tsi-tech-sheet"
CURRENT_PAGE_SOURCE = "vw-tcross-current-product-page"
MY26_MANUAL_SOURCE = "vw-tcross-my26-owner-manual"
PROBE_KEYS = (
    ("br-adjacent-incomplete-1.0", "br-hard-control-match-tcross-highline-complete-official-sources", "left"),
    ("br-adjacent-incomplete-1.0", "br-hard-control-match-tcross-highline-complete-official-sources", "right"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-current-page-missing-transmission-mapping", "left"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-current-page-missing-transmission-mapping", "right"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-model-year-present-one-side", "left"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-model-year-present-one-side", "right"),
)


def _mapping(case_id: str, side: str, field_sources: dict[str, list[str]]) -> dict:
    return {
        "benchmark": "catalog_identity_br_adjacent_incomplete_v1.json",
        "benchmarkDatasetVersion": "br-adjacent-incomplete-1.0",
        "caseId": case_id,
        "side": side,
        "fieldSourceIds": field_sources,
        "evidenceBasis": {
            GENERATION_SOURCE: "Retained Volkswagen do Brasil evidence establishes the Brazil T-Cross line beginning in 2019 and SUV context.",
            LAUNCH_SOURCE: "Retained launch evidence explicitly establishes Highline 250 TSI, Total Flex and six-speed automatic configuration.",
            TECH_SHEET_SOURCE: "Retained technical sheet explicitly establishes Highline 250 TSI, Total Flex and six-speed automatic configuration.",
            CURRENT_PAGE_SOURCE: "Retained current product page identifies Highline 250 TSI in the Brazil catalog.",
            MY26_MANUAL_SOURCE: "Retained MY26 owner manual establishes the model-year context plus 250 TSI Total Flex and AQ250 six-speed automatic mechanical family.",
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


PROBE_MAPPINGS = (
    _mapping(
        "br-hard-control-match-tcross-highline-complete-official-sources",
        "left",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [LAUNCH_SOURCE],
            "powertrain": [LAUNCH_SOURCE],
            "transmission": [LAUNCH_SOURCE],
            "body_style": [GENERATION_SOURCE],
            "market": [GENERATION_SOURCE],
        },
    ),
    _mapping(
        "br-hard-control-match-tcross-highline-complete-official-sources",
        "right",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [LAUNCH_SOURCE],
            "powertrain": [LAUNCH_SOURCE],
            "transmission": [LAUNCH_SOURCE],
            "body_style": [GENERATION_SOURCE],
            "market": [GENERATION_SOURCE],
        },
    ),
    _mapping(
        "br-hard-review-tcross-highline-current-page-missing-transmission-mapping",
        "left",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [LAUNCH_SOURCE],
            "powertrain": [LAUNCH_SOURCE],
            "transmission": [LAUNCH_SOURCE],
            "body_style": [GENERATION_SOURCE],
            "market": [GENERATION_SOURCE],
        },
    ),
    _mapping(
        "br-hard-review-tcross-highline-current-page-missing-transmission-mapping",
        "right",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [CURRENT_PAGE_SOURCE],
            "powertrain": [LAUNCH_SOURCE],
            "body_style": [GENERATION_SOURCE],
            "market": [GENERATION_SOURCE],
        },
    ),
    _mapping(
        "br-hard-review-tcross-highline-model-year-present-one-side",
        "left",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [TECH_SHEET_SOURCE],
            "powertrain": [TECH_SHEET_SOURCE],
            "transmission": [TECH_SHEET_SOURCE],
            "body_style": [GENERATION_SOURCE],
            "market": [GENERATION_SOURCE],
        },
    ),
    _mapping(
        "br-hard-review-tcross-highline-model-year-present-one-side",
        "right",
        {
            "make": [GENERATION_SOURCE],
            "model": [GENERATION_SOURCE],
            "generation": [GENERATION_SOURCE],
            "variant": [TECH_SHEET_SOURCE],
            "powertrain": [MY26_MANUAL_SOURCE],
            "transmission": [MY26_MANUAL_SOURCE],
            "body_style": [GENERATION_SOURCE],
            "market": [GENERATION_SOURCE],
            "model_year_from": [MY26_MANUAL_SOURCE],
            "model_year_to": [MY26_MANUAL_SOURCE],
        },
    ),
)


def _probe_records() -> list[dict]:
    payload = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-adjacent-tcross-1",
        "createdAt": "2026-09-01",
        "mappings": list(PROBE_MAPPINGS),
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return build_multisource_operational_records(ACTIVE_PATHS, path)


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class AdjacentTcrossMultisourceProbeTests(unittest.TestCase):
    def test_probe_builds_exact_six_field_complete_records(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 6)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        for record in records:
            self.assertGreaterEqual(len(record["sourceIds"]), 2)

    def test_probe_replays_after_retained_corpus_and_reports_dispositions(self) -> None:
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
        self.assertEqual(len(results), 6)
        self.assertTrue(all(result.action in allowed for result in results))

        actions = tuple(getattr(result.action, "value", str(result.action)) for result in results)
        published = len(store.catalog_vehicle_ids_page(after_id=None, limit=100))
        print(f"ADJACENT_TCROSS_PROBE_ACTIONS={actions}", flush=True)
        print(f"ADJACENT_TCROSS_PROBE_PUBLISHED={published}", flush=True)

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
