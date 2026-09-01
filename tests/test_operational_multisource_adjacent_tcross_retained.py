import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.operational_multisource import MULTISOURCE_REPLAY_METHOD
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
)
ADJACENT_KEYS = (
    ("br-adjacent-incomplete-1.0", "br-hard-control-match-tcross-highline-complete-official-sources", "left"),
    ("br-adjacent-incomplete-1.0", "br-hard-control-match-tcross-highline-complete-official-sources", "right"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-current-page-missing-transmission-mapping", "left"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-current-page-missing-transmission-mapping", "right"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-model-year-present-one-side", "left"),
    ("br-adjacent-incomplete-1.0", "br-hard-review-tcross-highline-model-year-present-one-side", "right"),
)


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class AdjacentTcrossRetainedRolloutTests(unittest.TestCase):
    def test_composed_measurement_promotes_exact_six_adjacent_sides(self) -> None:
        measurement = measure_combined_operational_provenance_eligibility_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        summary = measurement["summary"]
        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 44)
        self.assertEqual(summary["blockedRecords"], 16)
        self.assertEqual(summary["replayableByMethod"]["SOLE_CASE_SOURCE"], 12)
        self.assertEqual(summary["replayableByMethod"]["EXPLICIT_FIELD_ATTRIBUTION"], 10)
        self.assertEqual(summary["replayableByMethod"][MULTISOURCE_REPLAY_METHOD], 22)
        self.assertEqual(
            summary["blockedByReasonCode"],
            {
                "MISSING_SIDE_FIELD_ATTRIBUTION": 2,
                "MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION": 14,
            },
        )

        records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        self.assertEqual(len(records), 22)
        self.assertEqual(tuple(_key(record) for record in records[-6:]), ADJACENT_KEYS)

    def test_adjacent_sides_replay_after_retained_corpus_without_guessing_dispositions(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)

        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)

        records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        results = __import__(
            "podium7.operational_multisource",
            fromlist=["run_multisource_operational_records"],
        ).run_multisource_operational_records(store, records)

        self.assertEqual(len(results), 22)
        adjacent_records = records[-6:]
        adjacent_results = results[-6:]
        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertTrue(all(result.action in allowed for result in adjacent_results))
        self.assertGreaterEqual(len(store.catalog_vehicle_ids_page(after_id=None, limit=100)), 14)

        for record, result in zip(adjacent_records, adjacent_results):
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
