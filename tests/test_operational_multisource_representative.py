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
REPRESENTATIVE_KEY = (
    "br-1.0",
    "br-match-corolla-cross-xrx-hybrid-my25",
    "left",
)


class OperationalMultisourceRepresentativeTests(unittest.TestCase):
    def test_combined_measurement_promotes_only_the_validated_representative(self) -> None:
        measurement = measure_combined_operational_provenance_eligibility(
            ACTIVE_PATHS,
            ATTRIBUTION_PATH,
        )
        summary = measurement["summary"]
        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 23)
        self.assertEqual(summary["blockedRecords"], 37)
        self.assertEqual(summary["replayableByMethod"]["SOLE_CASE_SOURCE"], 12)
        self.assertEqual(summary["replayableByMethod"]["EXPLICIT_FIELD_ATTRIBUTION"], 10)
        self.assertEqual(summary["replayableByMethod"][MULTISOURCE_REPLAY_METHOD], 1)
        self.assertEqual(
            summary["blockedByReasonCode"],
            {
                "MISSING_SIDE_FIELD_ATTRIBUTION": 2,
                "MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION": 35,
            },
        )

        promoted = [
            record
            for record in measurement["records"]
            if record["method"] == MULTISOURCE_REPLAY_METHOD
        ]
        self.assertEqual(len(promoted), 1)
        self.assertEqual(
            (
                promoted[0]["datasetVersion"],
                promoted[0]["caseId"],
                promoted[0]["side"],
            ),
            REPRESENTATIVE_KEY,
        )
        self.assertEqual(
            promoted[0]["sourceIds"],
            ["toyota-corolla-cross-global-launch", "toyota-corolla-cross-my25-br"],
        )

    def test_representative_replays_after_existing_v1_corpus_without_losing_provenance(self) -> None:
        records = build_multisource_operational_records(ACTIVE_PATHS, ATTRIBUTION_PATH)
        self.assertEqual(len(records), 1)
        self.assertEqual(
            (records[0]["datasetVersion"], records[0]["caseId"], records[0]["side"]),
            REPRESENTATIVE_KEY,
        )

        store = CatalogStore()
        self.addCleanup(store.close)
        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)
        before_vehicle_ids = store.catalog_vehicle_ids_page(after_id=None, limit=100)
        self.assertEqual(len(before_vehicle_ids), 7)

        result = run_multisource_operational_records(store, records)[0]
        self.assertEqual(result.action, CatalogIngestionAction.CREATED)
        after_vehicle_ids = store.catalog_vehicle_ids_page(after_id=None, limit=100)
        self.assertEqual(len(after_vehicle_ids), 8)
        self.assertNotIn(result.vehicle_id, before_vehicle_ids)

        envelope_payload = records[0]["payload"]
        field_evidence = envelope_payload["provenance"]["fieldEvidence"]
        facts = store.catalog_candidates_for_entity(result.vehicle_id)
        actual_bindings = {(fact.attribute, fact.evidence_id) for fact in facts}
        expected_bindings = {
            (field_name, evidence_id)
            for field_name, evidence_ids in field_evidence.items()
            for evidence_id in evidence_ids
        }
        self.assertEqual(actual_bindings, expected_bindings)
        self.assertEqual(len(actual_bindings), 10)

        for fact in facts:
            evidence = store.get_raw_evidence(fact.evidence_id)
            self.assertIsNotNone(evidence)
            source = store.get_source(evidence.source_id)
            self.assertIsNotNone(source)
            self.assertIn(
                source.id,
                {
                    "toyota-corolla-cross-global-launch",
                    "toyota-corolla-cross-my25-br",
                },
            )


if __name__ == "__main__":
    unittest.main()
