from pathlib import Path
import unittest

from podium7.enrichment_quality import (
    evaluate_production_enrichment_quality_gate,
    measure_enriched_operational_corpus,
)
from podium7.source_backed_enrichment import (
    evaluate_source_backed_enrichment,
    load_source_backed_enrichment_overrides,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
ENRICHMENT_V3 = ROOT / "benchmarks" / "source_backed_enrichment_v3.json"
TCROSS_TRANSMISSION_EVIDENCE = (
    "operational:br-adjacent-incomplete-1.0:"
    "br-hard-review-tcross-highline-current-page-missing-transmission-mapping:right"
)
TCROSS_MODEL_YEAR_EVIDENCE = (
    "operational:br-adjacent-incomplete-1.0:"
    "br-hard-review-tcross-highline-model-year-present-one-side:right"
)


class ProductionEvidenceEnrichmentV3Tests(unittest.TestCase):
    def test_v3_resolves_tcross_transmission_without_policy_change(self) -> None:
        report = evaluate_source_backed_enrichment(DATASETS, ENRICHMENT_V3)

        self.assertEqual(report["summary"], {
            "observations": 7,
            "resolvedReviews": 3,
            "retainedReviews": 2,
            "incorrect": 0,
            "resolverPolicyChanges": 0,
        })

    def test_v3_applies_only_explicit_tcross_transmission(self) -> None:
        overrides = load_source_backed_enrichment_overrides(DATASETS, ENRICHMENT_V3)

        self.assertEqual(overrides[TCROSS_TRANSMISSION_EVIDENCE], {
            "transmission": "6-speed automatic",
        })
        self.assertNotIn(TCROSS_MODEL_YEAR_EVIDENCE, overrides)

    def test_v3_operational_replay_reduces_review_to_thirteen(self) -> None:
        measurement = measure_enriched_operational_corpus(DATASETS, ENRICHMENT_V3)

        self.assertEqual(measurement["summary"], {
            "total": 60,
            "created": 21,
            "matched": 26,
            "review": 13,
            "failed": 0,
            "openReviewTasks": 13,
            "appliedEvidenceOverrides": 4,
        })
        self.assertEqual(measurement["reviewCauses"], {
            "LABEL_AMBIGUITY": 3,
            "MISSING_IDENTITY_EVIDENCE": 10,
        })
        self.assertNotIn(TCROSS_TRANSMISSION_EVIDENCE, measurement["reviewReasonsByEvidence"])
        self.assertIn(TCROSS_MODEL_YEAR_EVIDENCE, measurement["reviewReasonsByEvidence"])

    def test_v3_integrated_gate_preserves_identity_safety(self) -> None:
        gate = evaluate_production_enrichment_quality_gate(DATASETS, ENRICHMENT_V3)

        self.assertTrue(gate["passed"])
        self.assertEqual(gate["identityQuality"]["metrics"]["autoMatchPrecision"], 1.0)
        self.assertEqual(gate["identityQuality"]["metrics"]["autoMatchRecall"], 1.0)
        self.assertEqual(gate["identityQuality"]["metrics"]["falseMergeCount"], 0)
        self.assertEqual(gate["identityQuality"]["metrics"]["ambiguousOvercommitCount"], 0)


if __name__ == "__main__":
    unittest.main()
