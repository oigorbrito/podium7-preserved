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
BASELINE_ATTRIBUTION_PATHS = ATTRIBUTION_PATHS[:-1]
YEAR_CASE = "br-no-match-corsa-shared-fipe-different-model-year"
REVIEW_CASE = "br-review-shared-fipe-code-alone"
CORSA_KEYS = (
    ("br-1.0", YEAR_CASE, "left"),
    ("br-1.0", YEAR_CASE, "right"),
    ("br-1.0", REVIEW_CASE, "left"),
    ("br-1.0", REVIEW_CASE, "right"),
)
SECONDARY_SOURCE = "corsa-wind-fipe-code-secondary"
EXPECTED_SOURCE_IDS = {
    "fipe-official-vehicle-index",
    "tce-pr-fipe-model-table-2015",
    "detran-rr-leilao-004-2025-corsa-1995",
    "detran-rr-leilao-003-2025-corsa-1997",
}


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class CorsaRetainedRolloutTests(unittest.TestCase):
    def test_corsa_overlay_closes_exact_prior_four_record_gap(self) -> None:
        baseline = measure_combined_operational_provenance_eligibility_from_overlays(
            ACTIVE_PATHS,
            BASELINE_ATTRIBUTION_PATHS,
        )["summary"]
        self.assertEqual(baseline["records"], 60)
        self.assertEqual(baseline["replayableRecords"], 56)
        self.assertEqual(baseline["blockedRecords"], 4)
        self.assertEqual(
            baseline["blockedByReasonCode"],
            {"MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION": 4},
        )

        current = measure_combined_operational_provenance_eligibility_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )["summary"]
        self.assertEqual(current["records"], 60)
        self.assertEqual(current["replayableRecords"], 60)
        self.assertEqual(current["blockedRecords"], 0)
        self.assertEqual(current["blockedByReasonCode"], {})

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

        for record, result in zip(records[-4:], results[-4:]):
            if result.action is CatalogIngestionAction.REVIEW:
                self.assertIsNotNone(result.review_id)
                self.assertIsNone(result.vehicle_id)
                continue
            self.assertIsNotNone(result.vehicle_id)
            field_evidence = record["payload"]["provenance"]["fieldEvidence"]
            self.assertTrue(field_evidence)
            self.assertIn("market", field_evidence)
            self.assertIn("external_identifiers", field_evidence)
            expected_bindings = {
                (field_name, evidence_id)
                for field_name, evidence_ids in field_evidence.items()
                for evidence_id in evidence_ids
            }
            actual_bindings = {
                (fact.attribute, fact.evidence_id)
                for fact in store.catalog_candidates_for_entity(result.vehicle_id)
            }
            self.assertTrue(expected_bindings <= actual_bindings)
            evidence_source_ids = {
                store.get_raw_evidence(evidence_id).source_id
                for _, evidence_id in expected_bindings
            }
            self.assertTrue(evidence_source_ids <= EXPECTED_SOURCE_IDS)


if __name__ == "__main__":
    unittest.main()
