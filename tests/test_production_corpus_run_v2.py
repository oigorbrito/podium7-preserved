from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_api import list_catalog_vehicles
from podium7.operational_provenance import (
    build_provenance_eligible_operational_records,
    measure_operational_provenance_eligibility,
    run_provenance_eligible_operational_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionCorpusRunV2Tests(unittest.TestCase):
    def test_expanded_source_backed_corpus_runs_end_to_end(self) -> None:
        eligibility = measure_operational_provenance_eligibility(DATASETS)["summary"]
        records = build_provenance_eligible_operational_records(DATASETS)

        self.assertEqual(eligibility["records"], 60)
        self.assertEqual(len(records), eligibility["replayableRecords"])
        self.assertGreater(eligibility["replayableRecords"], 0)
        self.assertGreater(eligibility["blockedRecords"], 0)
        self.assertTrue(all(record["evidence"]["locator"].startswith("https://") for record in records))

        store = CatalogStore()
        report = run_provenance_eligible_operational_corpus(store, DATASETS)
        self.assertTrue(report.ok)
        self.assertEqual(report.total, eligibility["replayableRecords"])
        self.assertEqual(report.failed, 0)
        self.assertEqual(report.created + report.matched + report.review, report.total)
        self.assertGreater(report.created, 0)
        self.assertGreater(report.matched, 0)
        self.assertGreater(report.review, 0)

        consumer = list_catalog_vehicles(store, limit=100)
        self.assertTrue(consumer["ok"])
        self.assertGreater(len(consumer["items"]), 0)

        print(
            "PRODUCTION_CORPUS_RUN_V2_PROVENANCE_GATED",
            {
                "retainedRecords": eligibility["records"],
                "replayableRecords": eligibility["replayableRecords"],
                "blockedRecords": eligibility["blockedRecords"],
                "total": report.total,
                "created": report.created,
                "matched": report.matched,
                "review": report.review,
                "failed": report.failed,
                "consumerItems": len(consumer["items"]),
            },
        )


if __name__ == "__main__":
    unittest.main()
