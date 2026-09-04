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
    "benchmarks/operational_multisource_field_attribution_onix_v1.json",
    "benchmarks/operational_multisource_field_attribution_mustang_v1.json",
    "benchmarks/operational_multisource_field_attribution_toyota_porsche_v1.json",
    "benchmarks/operational_multisource_field_attribution_corsa_v1.json",
)
CORSA_KEYS = (
    ("br-1.0", "br-no-match-corsa-shared-fipe-different-model-year", "left"),
    ("br-1.0", "br-no-match-corsa-shared-fipe-different-model-year", "right"),
    ("br-1.0", "br-review-shared-fipe-code-alone", "left"),
    ("br-1.0", "br-review-shared-fipe-code-alone", "right"),
)
CORSA_SECONDARY_SOURCE = "corsa-wind-fipe-code-secondary"
EXPECTED_SOURCE_IDS = {
    "fipe-official-vehicle-index",
    "tce-pr-fipe-model-table-2015",
    "detran-rr-leilao-004-2025-corsa-1995",
    "detran-rr-leilao-003-2025-corsa-1997",
}


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
        self.assertEqual(tuple(_key(record) for record in records[-4:]), CORSA_KEYS)
        for record in records[-4:]:
            self.assertNotIn(CORSA_SECONDARY_SOURCE, record["sourceIds"])
            self.assertTrue(set(record["sourceIds"]) >= {"fipe-official-vehicle-index", "tce-pr-fipe-model-table-2015"})

    def test_corsa_sides_replay_after_retained_corpus_with_complete_field_provenance(self) -> None:
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

        self.assertEqual(len(results), 38)
        corsa_records = records[-4:]
        corsa_results = results[-4:]
        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertTrue(all(result.action in allowed for result in corsa_results))

        for record, result in zip(corsa_records, corsa_results):
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
