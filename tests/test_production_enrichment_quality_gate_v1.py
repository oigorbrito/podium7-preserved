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
    def test_enriched_replay_is_measured_only_on_provenance_eligible_records(self) -> None:
        measurement = measure_enriched_operational_corpus(DATASETS, ENRICHMENT)
        summary = measurement["summary"]
        eligibility = measurement["provenanceEligibility"]

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
        self.assertEqual(summary["appliedEvidenceOverrides"], 1)
        self.assertEqual(sum(measurement["reviewCauses"].values()), summary["review"])
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", measurement["reviewCauses"])

    def test_integrated_quality_gate_preserves_identity_safety(self) -> None:
        gate = evaluate_production_enrichment_quality_gate(DATASETS, ENRICHMENT)

        self.assertTrue(gate["passed"])
        self.assertTrue(all(gate["checks"].values()))
        self.assertEqual(
            gate["baselineOperational"]["provenanceEligibility"],
            gate["operational"]["provenanceEligibility"],
        )
        self.assertLessEqual(gate["operationalReviewDelta"], 0)
        metrics = gate["identityQuality"]["metrics"]
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)
        self.assertEqual(gate["enrichment"]["summary"]["resolvedReviews"], 1)
        self.assertEqual(gate["enrichment"]["summary"]["resolverPolicyChanges"], 0)


if __name__ == "__main__":
    unittest.main()
