from pathlib import Path
import json
import tempfile
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
ENRICHMENT_V2 = ROOT / "benchmarks" / "source_backed_enrichment_v2.json"
SPARSE_ONIX_EVIDENCE = "operational:br-adjacent-incomplete-1.0:br-hard-no-match-onix-premier-my26-vs-my27:left"
LATER_ONIX_EVIDENCE = "operational:br-adjacent-incomplete-1.0:br-hard-review-onix-my26-premier-incomplete-mechanical-mapping:right"


class ProductionEvidenceEnrichmentV2Tests(unittest.TestCase):
    def test_v2_resolves_reviews_and_preserves_explicit_abstentions(self) -> None:
        report = evaluate_source_backed_enrichment(DATASETS, ENRICHMENT_V2)

        self.assertEqual(report["summary"], {
            "observations": 6,
            "resolvedReviews": 2,
            "retainedReviews": 2,
            "incorrect": 0,
            "resolverPolicyChanges": 0,
        })

    def test_v2_merges_non_overlapping_source_evidence_for_sparse_record(self) -> None:
        overrides = load_source_backed_enrichment_overrides(DATASETS, ENRICHMENT_V2)

        self.assertEqual(overrides[SPARSE_ONIX_EVIDENCE], {
            "powertrain": "1.0 turbo",
            "transmission": "6-speed automatic",
            "body_style": "hatch",
            "generation": "2nd generation",
        })
        self.assertEqual(overrides[LATER_ONIX_EVIDENCE], {
            "powertrain": "1.0 turbo",
            "transmission": "6-speed automatic",
        })

    def test_source_outside_curated_case_is_rejected(self) -> None:
        payload = json.loads(ENRICHMENT_V2.read_text(encoding="utf-8"))
        observation = next(
            item
            for item in payload["observations"]
            if item["id"] == "chevrolet-onix-my26-sparse-record-generation-enrichment"
        )
        observation["sourceId"] = "vw-tcross-brazil-generation"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source is not declared by the benchmark case"):
                load_source_backed_enrichment_overrides(DATASETS, path)

    def test_v2_operational_replay_reduces_review_to_nineteen(self) -> None:
        measurement = measure_enriched_operational_corpus(DATASETS, ENRICHMENT_V2)

        self.assertEqual(measurement["summary"], {
            "total": 60,
            "created": 19,
            "matched": 22,
            "review": 19,
            "failed": 0,
            "openReviewTasks": 19,
            "appliedEvidenceOverrides": 3,
        })
        self.assertEqual(measurement["reviewCauses"], {
            "LABEL_AMBIGUITY": 9,
            "MISSING_IDENTITY_EVIDENCE": 10,
        })
        self.assertNotIn(SPARSE_ONIX_EVIDENCE, measurement["reviewReasonsByEvidence"])
        self.assertNotIn(LATER_ONIX_EVIDENCE, measurement["reviewReasonsByEvidence"])

    def test_v2_integrated_gate_preserves_identity_safety(self) -> None:
        gate = evaluate_production_enrichment_quality_gate(DATASETS, ENRICHMENT_V2)

        self.assertTrue(gate["passed"])
        self.assertEqual(gate["identityQuality"]["metrics"]["autoMatchPrecision"], 1.0)
        self.assertEqual(gate["identityQuality"]["metrics"]["autoMatchRecall"], 1.0)
        self.assertEqual(gate["identityQuality"]["metrics"]["falseMergeCount"], 0)
        self.assertEqual(gate["identityQuality"]["metrics"]["ambiguousOvercommitCount"], 0)


if __name__ == "__main__":
    unittest.main()
