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
)
TOYOTA_KEY = ("1.0", "no-match-toyota-corolla-10g-vs-12g", "left")
PORSCHE_KEY = ("1.0", "no-match-porsche-911-991-vs-992", "left")
TOYOTA_COROLLA_SOURCE = "toyota-corolla-2006-global"
TOYOTA_FUEL_SOURCE = "toyota-2zr-fe-gasoline-2006"
PORSCHE_GENERATION_SOURCE = "porsche-911-generations-2019"
PORSCHE_TECH_SPEC_SOURCE = "porsche-911-carrera-s-991-tech-spec"


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


def _sources_by_field(record: dict) -> dict[str, list[str]]:
    return {
        field: [evidence_id.rsplit(":", 1)[1] for evidence_id in evidence_ids]
        for field, evidence_ids in record["payload"]["provenance"]["fieldEvidence"].items()
    }


def _common_field_source(field_source_ids: dict[str, list[str]]) -> set[str]:
    return set.intersection(*(set(source_ids) for source_ids in field_source_ids.values()))


class ToyotaPorscheRetainedRolloutTests(unittest.TestCase):
    def test_composed_measurement_promotes_exact_two_toyota_porsche_sides(self) -> None:
        measurement = measure_combined_operational_provenance_eligibility_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        summary = measurement["summary"]
        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 56)
        self.assertEqual(summary["blockedRecords"], 4)
        self.assertEqual(summary["replayableByMethod"]["SOLE_CASE_SOURCE"], 12)
        self.assertEqual(summary["replayableByMethod"]["EXPLICIT_FIELD_ATTRIBUTION"], 10)
        self.assertEqual(summary["replayableByMethod"][MULTISOURCE_REPLAY_METHOD], 34)
        self.assertEqual(
            summary["blockedByReasonCode"],
            {"MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION": 4},
        )

        records = build_multisource_operational_records_from_overlays(
            ACTIVE_PATHS,
            ATTRIBUTION_PATHS,
        )
        self.assertEqual(len(records), 34)
        self.assertEqual(tuple(_key(record) for record in records[-2:]), (TOYOTA_KEY, PORSCHE_KEY))

        toyota_sources = _sources_by_field(records[-2])
        self.assertEqual(_common_field_source(toyota_sources), set())
        self.assertEqual(toyota_sources["powertrain"], [TOYOTA_FUEL_SOURCE])
        self.assertNotIn(TOYOTA_COROLLA_SOURCE, toyota_sources["powertrain"])

        porsche_sources = _sources_by_field(records[-1])
        self.assertEqual(_common_field_source(porsche_sources), set())
        self.assertEqual(porsche_sources["generation"], [PORSCHE_GENERATION_SOURCE])
        self.assertNotIn(PORSCHE_TECH_SPEC_SOURCE, porsche_sources["generation"])

    def test_toyota_porsche_sides_replay_with_complete_field_provenance(self) -> None:
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

        self.assertEqual(len(results), 34)
        target_records = records[-2:]
        target_results = results[-2:]
        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertTrue(all(result.action in allowed for result in target_results))

        for record, result in zip(target_records, target_results):
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
