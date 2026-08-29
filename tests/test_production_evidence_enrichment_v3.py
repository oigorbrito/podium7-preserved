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

    def test_v3_operational_replay_is_provenance_gated(self) -> None:
        measurement = measure_enriched_operational_corpus(DATASETS, ENRICHMENT_V3)
        summary = measurement["summary"]
        eligibility = measurement["provenanceEligibility"]
        scope = measurement["enrichmentScope"]
        overrides = load_source_backed_enrichment_overrides(DATASETS, ENRICHMENT_V3)

        self.assertEqual(eligibility["records"], 60)
        self.assertEqual(
            eligibility["records"],
            eligibility["replayableRecords"] + eligibility["blockedRecords"],
        )
        self.assertGreater(eligibility["blockedRecords"], 0)
        self.assertEqual(summary["total"], eligibility["replayableRecords"])
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(
            summary["created"] + summary["matched"] + summary["review"],
            summary["total"],
        )
        self.assertEqual(summary["openReviewTasks"], summary["review"])
        self.assertEqual(scope["evidenceOverrides"], len(overrides))
        self.assertEqual(
            scope["evidenceOverrides"],
            scope["appliedEvidenceOverrides"] + scope["excludedEvidenceOverrides"],
        )
        self.assertEqual(summary["appliedEvidenceOverrides"], scope["appliedEvidenceOverrides"])
        self.assertEqual(summary["excludedEvidenceOverrides"], scope["excludedEvidenceOverrides"])
        self.assertGreater(scope["excludedEvidenceOverrides"], 0)
        self.assertIn(TCROSS_TRANSMISSION_EVIDENCE, scope["excludedEvidenceOverrideIds"])
        self.assertEqual(sum(measurement["reviewCauses"].values()), summary["review"])
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", measurement["reviewCauses"])
        self.assertNotIn(TCROSS_TRANSMISSION_EVIDENCE, measurement["reviewReasonsByEvidence"])

    def test_v3_integrated_gate_preserves_identity_safety(self) -> None:
        gate = evaluate_production_enrichment_quality_gate(DATASETS, ENRICHMENT_V3)

        self.assertTrue(gate["passed"])
        self.assertTrue(all(gate["checks"].values()))
        self.assertEqual(
            gate["baselineOperational"]["provenanceEligibility"],
            gate["operational"]["provenanceEligibility"],
        )
        self.assertLessEqual(gate["operationalReviewDelta"], 0)
        self.assertEqual(gate["enrichment"]["summary"]["resolvedReviews"], 3)
        self.assertEqual(gate["identityQuality"]["metrics"]["autoMatchPrecision"], 1.0)
        self.assertEqual(gate["identityQuality"]["metrics"]["autoMatchRecall"], 1.0)
        self.assertEqual(gate["identityQuality"]["metrics"]["falseMergeCount"], 0)
        self.assertEqual(gate["identityQuality"]["metrics"]["ambiguousOvercommitCount"], 0)


if __name__ == "__main__":
    unittest.main()
