from pathlib import Path
import unittest

from podium7.enrichment_quality import (
    evaluate_production_enrichment_quality_gate,
    measure_enriched_operational_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
ENRICHMENT = ROOT / "benchmarks" / "source_backed_enrichment_v1.json"


class ProductionEnrichmentQualityGateV1Tests(unittest.TestCase):
    def test_enriched_replay_reduces_review_only_by_source_backed_evidence(self) -> None:
        measurement = measure_enriched_operational_corpus(DATASETS, ENRICHMENT)

        self.assertEqual(measurement["summary"], {
            "total": 12,
            "created": 4,
            "matched": 5,
            "review": 3,
            "failed": 0,
            "openReviewTasks": 3,
            "appliedEvidenceOverrides": 1,
        })
        self.assertEqual(measurement["reviewCauses"], {
            "LABEL_AMBIGUITY": 1,
            "MISSING_IDENTITY_EVIDENCE": 2,
        })

    def test_integrated_quality_gate_preserves_identity_safety(self) -> None:
        gate = evaluate_production_enrichment_quality_gate(DATASETS, ENRICHMENT)

        self.assertTrue(gate["passed"])
        self.assertTrue(all(gate["checks"].values()))
        metrics = gate["identityQuality"]["metrics"]
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertEqual(gate["enrichment"]["summary"]["resolvedReviews"], 1)
        self.assertEqual(gate["enrichment"]["summary"]["resolverPolicyChanges"], 0)


if __name__ == "__main__":
    unittest.main()
