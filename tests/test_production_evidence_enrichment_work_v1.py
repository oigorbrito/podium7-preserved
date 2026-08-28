from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_operational import run_source_backed_operational_corpus
from podium7.evidence_enrichment import build_source_backed_enrichment_work


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionEvidenceEnrichmentWorkV1Tests(unittest.TestCase):
    def test_all_measured_reviews_become_source_backed_work_without_policy_change(self) -> None:
        store = CatalogStore()
        report = run_source_backed_operational_corpus(store, DATASETS)
        self.assertEqual(report.review, 4)

        work = build_source_backed_enrichment_work(store, DATASETS)

        self.assertEqual(work["summary"], {
            "openReviews": 4,
            "actionable": 4,
            "blocked": 0,
            "resolverPolicyChanges": 0,
        })
        self.assertEqual(work["causeCounts"], {
            "LABEL_AMBIGUITY": 1,
            "MISSING_IDENTITY_EVIDENCE": 3,
        })
        self.assertEqual(work["blockedItems"], [])
        self.assertTrue(all(item["sourceLocators"] for item in work["items"]))
        self.assertTrue(all(item["resolverPolicyChange"] is False for item in work["items"]))


if __name__ == "__main__":
    unittest.main()
