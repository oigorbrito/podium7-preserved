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
        self.assertEqual(report.review, 22)

        work = build_source_backed_enrichment_work(store, DATASETS)

        self.assertEqual(work["summary"], {
            "openReviews": 22,
            "actionable": 22,
            "blocked": 0,
            "resolverPolicyChanges": 0,
        })
        self.assertEqual(work["causeCounts"], {
            "LABEL_AMBIGUITY": 9,
            "MISSING_IDENTITY_EVIDENCE": 13,
        })
        self.assertEqual(work["blockedItems"], [])
        self.assertTrue(all(item["sourceLocators"] for item in work["items"]))
        self.assertTrue(all(item["resolverPolicyChange"] is False for item in work["items"]))

    def test_multi_source_case_preserves_every_source_locator_for_enrichment(self) -> None:
        store = CatalogStore()
        run_source_backed_operational_corpus(store, DATASETS)
        work = build_source_backed_enrichment_work(store, DATASETS)

        multi_source = [
            item
            for item in work["items"]
            if len(item["sourceIds"]) > 1
        ]
        self.assertTrue(multi_source)
        for item in multi_source:
            self.assertEqual(len(item["sourceIds"]), len(item["sourceLocators"]))
            self.assertEqual(len(item["sourceIds"]), len(set(item["sourceIds"])))
            self.assertTrue(all(locator.startswith("https://") for locator in item["sourceLocators"]))


if __name__ == "__main__":
    unittest.main()
