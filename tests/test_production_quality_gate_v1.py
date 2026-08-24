from __future__ import annotations

import json
from pathlib import Path
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_api import list_catalog_vehicles
from podium7.catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload
from podium7.catalog_quality import analyze_review_cases, evaluate_identity_quality


ROOT = Path(__file__).resolve().parents[1]
QUALITY_DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
CORPUS = ROOT / "benchmarks" / "production_end_to_end_corpus_v1.json"


class ProductionQualityGateV1Tests(unittest.TestCase):
    def test_operational_corpus_and_identity_quality_pass_together(self) -> None:
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
        store = CatalogStore()
        report = ingest_catalog_batch(
            store,
            parse_catalog_batch_payload({"records": corpus["records"]}),
        )

        self.assertTrue(report.ok)
        self.assertEqual(report.failed, 0)
        self.assertEqual(report.total, corpus["expected"]["total"])
        self.assertEqual(report.created, corpus["expected"]["created"])
        self.assertEqual(report.matched, corpus["expected"]["matched"])
        self.assertEqual(report.review, corpus["expected"]["review"])
        consumer = list_catalog_vehicles(store, limit=100)
        self.assertTrue(consumer["ok"])
        self.assertEqual(len(consumer["items"]), corpus["expected"]["consumerItems"])

        quality = evaluate_identity_quality(QUALITY_DATASETS)
        metrics = quality["metrics"]
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedMatchCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)

        review_analysis = analyze_review_cases(quality)
        self.assertEqual(review_analysis["unknownCauseCount"], 0)
        self.assertEqual(review_analysis["unexpectedReviewCount"], 0)
        self.assertFalse(review_analysis["resolverChangeRequired"])
        self.assertTrue(
            all(
                case["disposition"] in {"ENRICH_THEN_REVIEW", "HUMAN_REVIEW_REQUIRED"}
                for case in review_analysis["cases"]
            )
        )


if __name__ == "__main__":
    unittest.main()
