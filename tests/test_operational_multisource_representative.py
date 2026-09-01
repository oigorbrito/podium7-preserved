import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.operational_multisource import (
    MULTISOURCE_REPLAY_METHOD,
    build_multisource_operational_records,
    measure_combined_operational_provenance_eligibility,
    run_multisource_operational_records,
)
from podium7.operational_provenance import run_provenance_eligible_operational_corpus


ACTIVE_PATHS = (
    "benchmarks/catalog_identity_golden_v1.json",
    "benchmarks/catalog_identity_golden_br_v1.json",
    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
)
ATTRIBUTION_PATH = "benchmarks/operational_multisource_field_attribution_v1.json"
COROLLA_CROSS_KEYS = (
    ("br-1.0", "br-match-corolla-cross-xrx-hybrid-my25", "left"),
    ("br-1.0", "br-match-corolla-cross-xrx-hybrid-my25", "right"),
    ("br-1.0", "br-no-match-corolla-cross-xrx-hybrid-vs-xrx-flex", "left"),
    ("br-1.0", "br-no-match-corolla-cross-xrx-hybrid-vs-xrx-flex", "right"),
    ("br-1.0", "br-review-corolla-cross-xrx-hybrid-missing-variant", "left"),
    ("br-1.0", "br-review-corolla-cross-xrx-hybrid-missing-variant", "right"),
)
TCROSS_KEYS = (
    ("br-1.0", "br-match-tcross-highline-250-tsi", "left"),
    ("br-1.0", "br-match-tcross-highline-250-tsi", "right"),
    ("br-1.0", "br-no-match-tcross-highline-vs-comfortline", "left"),
    ("br-1.0", "br-no-match-tcross-highline-vs-comfortline", "right"),
    ("br-1.0", "br-review-tcross-250-tsi-missing-variant", "left"),
    ("br-1.0", "br-review-tcross-250-tsi-missing-variant", "right"),
)
OVERLAY_KEYS = COROLLA_CROSS_KEYS + TCROSS_KEYS
COROLLA_CROSS_SOURCES = {
    "toyota-corolla-cross-global-launch",
    "toyota-corolla-cross-my25-br",
}
TCROSS_SOURCES = {
    "vw-tcross-2019-br-generation",
    "vw-tcross-current-config",
}


def _record_key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


def _expected_sources(record: dict) -> set[str]:
    return TCROSS_SOURCES if _record_key(record) in TCROSS_KEYS else COROLLA_CROSS_SOURCES


class OperationalMultisourceRolloutTests(unittest.TestCase):
    def test_combined_measurement_promotes_exact_two_source_families(self) -> None:
        measurement = measure_combined_operational_provenance_eligibility(
            ACTIVE_PATHS,
            ATTRIBUTION_PATH,
        )
        summary = measurement["summary"]
        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 34)
        self.assertEqual(summary["blockedRecords"], 26)
        self.assertEqual(summary["replayableByMethod"]["SOLE_CASE_SOURCE"], 12)
        self.assertEqual(summary["replayableByMethod"]["EXPLICIT_FIELD_ATTRIBUTION"], 10)
        self.assertEqual(summary["replayableByMethod"][MULTISOURCE_REPLAY_METHOD], 12)
        self.assertEqual(
            summary["blockedByReasonCode"],
            {
                "MISSING_SIDE_FIELD_ATTRIBUTION": 2,
                "MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION": 24,
            },
        )

        promoted = [
            record
            for record in measurement["records"]
            if record["method"] == MULTISOURCE_REPLAY_METHOD
        ]
        self.assertEqual(len(promoted), 12)
        self.assertEqual({_record_key(record) for record in promoted}, set(OVERLAY_KEYS))
        for record in promoted:
            self.assertEqual(set(record["sourceIds"]), _expected_sources(record))

    def test_every_overlay_replays_in_isolation_with_exact_provenance(self) -> None:
        records = build_multisource_operational_records(ACTIVE_PATHS, ATTRIBUTION_PATH)
        self.assertEqual(len(records), 12)
        self.assertEqual(tuple(_record_key(record) for record in records), OVERLAY_KEYS)

        for record in records:
            with self.subTest(caseId=record["caseId"], side=record["side"]):
                store = CatalogStore()
                try:
                    result = run_multisource_operational_records(store, (record,))[0]
                    self.assertEqual(result.action, CatalogIngestionAction.CREATED)
                    self.assertIsNotNone(result.vehicle_id)

                    field_evidence = record["payload"]["provenance"]["fieldEvidence"]
                    expected_bindings = {
                        (field_name, evidence_id)
                        for field_name, evidence_ids in field_evidence.items()
                        for evidence_id in evidence_ids
                    }
                    facts = store.catalog_candidates_for_entity(result.vehicle_id)
                    actual_bindings = {(fact.attribute, fact.evidence_id) for fact in facts}
                    self.assertEqual(actual_bindings, expected_bindings)

                    expected_sources = _expected_sources(record)
                    for fact in facts:
                        evidence = store.get_raw_evidence(fact.evidence_id)
                        self.assertIsNotNone(evidence)
                        source = store.get_source(evidence.source_id)
                        self.assertIsNotNone(source)
                        self.assertIn(source.id, expected_sources)
                finally:
                    store.close()

    def test_two_families_replay_after_existing_v1_corpus_with_expected_dispositions(self) -> None:
        records = build_multisource_operational_records(ACTIVE_PATHS, ATTRIBUTION_PATH)
        store = CatalogStore()
        self.addCleanup(store.close)

        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)
        self.assertEqual(len(store.catalog_vehicle_ids_page(after_id=None, limit=100)), 7)

        results = run_multisource_operational_records(store, records)
        family_actions = (
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        )
        self.assertEqual(tuple(result.action for result in results), family_actions + family_actions)
        self.assertEqual(len(store.catalog_vehicle_ids_page(after_id=None, limit=100)), 11)
        self.assertIsNotNone(results[5].review_id)
        self.assertIsNone(results[5].vehicle_id)
        self.assertIsNotNone(results[11].review_id)
        self.assertIsNone(results[11].vehicle_id)

        for record, result in zip(records, results):
            if result.vehicle_id is None:
                continue
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
