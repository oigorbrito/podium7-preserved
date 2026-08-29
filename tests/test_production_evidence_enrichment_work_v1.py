from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.evidence_enrichment import build_source_backed_enrichment_work
from podium7.operational_provenance import (
    measure_operational_provenance_eligibility,
    run_provenance_eligible_operational_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionEvidenceEnrichmentWorkV1Tests(unittest.TestCase):
    def test_all_measured_reviews_become_source_backed_work_without_policy_change(self) -> None:
        eligibility = measure_operational_provenance_eligibility(DATASETS)["summary"]
        store = CatalogStore()
        report = run_provenance_eligible_operational_corpus(store, DATASETS)
        self.assertEqual(report.total, eligibility["replayableRecords"])
        self.assertGreater(report.review, 0)
        self.assertGreater(eligibility["blockedRecords"], 0)

        work = build_source_backed_enrichment_work(store, DATASETS)

        self.assertEqual(work["summary"]["openReviews"], report.review)
        self.assertEqual(
            work["summary"]["openReviews"],
            work["summary"]["actionable"] + work["summary"]["blocked"],
        )
        self.assertEqual(work["summary"]["resolverPolicyChanges"], 0)
        self.assertTrue(all(item["sourceLocators"] for item in work["items"]))
        self.assertTrue(all(item["resolverPolicyChange"] is False for item in work["items"]))

    def test_ambiguous_multi_source_sides_remain_blocked_before_enrichment(self) -> None:
        eligibility = measure_operational_provenance_eligibility(DATASETS)
        blocked = [item for item in eligibility["records"] if not item["replayable"]]

        self.assertTrue(blocked)
        self.assertTrue(
            any("multiple sourceIds" in item["reason"] for item in blocked)
        )
        self.assertTrue(all(item["sourceId"] is None for item in blocked))


if __name__ == "__main__":
    unittest.main()
