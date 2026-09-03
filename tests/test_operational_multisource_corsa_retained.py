import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.operational_multisource import MULTISOURCE_REPLAY_METHOD, run_multisource_operational_records
from podium7.operational_multisource_overlay_set import (
    build_multisource_operational_records_from_overlays,
    measure_combined_operational_provenance_eligibility_from_overlays,
)
from podium7.operational_provenance import run_provenance_eligible_operational_corpus


ACTIVE_PATHS = (
    "benchmarks/catalog_identity_golden_v1.json",
    "benchmarks/catalog_identity_golden_br_v1.json",
    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
)
ATTRIBUTION_PATHS = (
    "benchmarks/operational_multisource_field_attribution_v1.json",
    "benchmarks/operational_multisource_field_attribution_tcross_adjacent_v1.json",
    "benchmarks/operational_multisource_field_attribution_onix_v1.json",
    "benchmarks/operational_multisource_field_attribution_mustang_v1.json",
    "benchmarks/operational_multisource_field_attribution_toyota_porsche_v1.json",
    "benchmarks/operational_multisource_field_attribution_corsa_v1.json",
)
YEAR_CASE = "br-no-match-corsa-shared-fipe-different-model-year"
REVIEW_CASE = "br-review-shared-fipe-code-alone"
CORSA_KEYS = (
    ("br-1.0", YEAR_CASE, "left"),
    ("br-1.0", YEAR_CASE, "right"),
    ("br-1.0", REVIEW_CASE, "left"),
    ("br-1.0", REVIEW_CASE, "right"),
)
SECONDARY_SOURCE = "corsa-wind-fipe-code-secondary"


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class CorsaRetainedRolloutTests(unittest.TestCase):
    def test_composed_measurement_promotes_exact_four_corsa_sides(self) -> None:
        measurement = measure_combined_operational_provenance_eligibility_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        summary = measurement["summary"]
        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 60)
        self.assertEqual(summary["blockedRecords"], 0)
        self.assertEqual(summary["replayableByMethod"]["SOLE_CASE_SOURCE"], 12)
        self.assertEqual(summary["replayableByMethod"]["EXPLICIT_FIELD_ATTRIBUTION"], 10)
        self.assertEqual(summary["replayableByMethod"][MULTISOURCE_REPLAY_METHOD], 38)
        self.assertEqual(summary["blockedByReasonCode"], {})

        records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        self.assertEqual(len(records), 38)
        corsa_records = records[-4:]
        self.assertEqual(tuple(_key(record) for record in corsa_records), CORSA_KEYS)
        for record in corsa_records:
            self.assertNotIn(SECONDARY_SOURCE, record["sourceIds"])
            self.assertGreaterEqual(len(record["sourceIds"]), 2)
            field_evidence = record["payload"]["provenance"]["fieldEvidence"]
            self.assertEqual(set(field_evidence), set(record["payload"]["vehicle"]))
            self.assertTrue(all(field_evidence[field] for field in field_evidence))

    def test_corsa_sides_replay_from_retained_repository_files(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)

        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)

        records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        self.assertEqual(tuple(_key(record) for record in records[-4:]), CORSA_KEYS)
        results = run_multisource_operational_records(store, records)
        self.assertEqual(len(results), 38)

        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertTrue(all(result.action in allowed for result in results[-4:]))


if __name__ == "__main__":
    unittest.main()
