import unittest

from podium7.catalog import CatalogMatchOutcome
from podium7.er_pipeline_benchmark import (
    ERPipelineCase,
    ERPipelineCost,
    ERPipelineScale,
    evaluate_er_pipeline,
)


class ERPipelineBenchmarkTests(unittest.TestCase):
    def test_reports_blocking_verification_end_to_end_and_cost_metrics(self):
        report = evaluate_er_pipeline(
            [
                ERPipelineCase("match-kept", CatalogMatchOutcome.MATCH, True, CatalogMatchOutcome.MATCH),
                ERPipelineCase("match-filtered", CatalogMatchOutcome.MATCH, False, None),
                ERPipelineCase("no-match-kept", CatalogMatchOutcome.NO_MATCH, True, CatalogMatchOutcome.NO_MATCH),
                ERPipelineCase("review-kept", CatalogMatchOutcome.REVIEW, True, CatalogMatchOutcome.REVIEW),
            ],
            cost=ERPipelineCost(latency_ms=25, peak_memory_bytes=4096),
            scale=ERPipelineScale(candidate_universe_size=100, retained_candidate_count=20),
        )
        metrics = report["metrics"]
        self.assertEqual(0.25, metrics["labeledPairReductionRatio"])
        self.assertEqual(0.8, metrics["candidateReductionRatio"])
        self.assertEqual(100, metrics["candidateUniverseSize"])
        self.assertEqual(20, metrics["retainedCandidateCount"])
        self.assertEqual(0.5, metrics["blockingRecall"])
        self.assertEqual(1.0, metrics["verificationPrecision"])
        self.assertEqual(1.0, metrics["verificationRecall"])
        self.assertEqual(1.0, metrics["endToEndMatchPrecision"])
        self.assertEqual(0.5, metrics["endToEndMatchRecall"])
        self.assertEqual(0, metrics["falseMergeCount"])
        self.assertEqual(1, metrics["missedMatchCount"])
        self.assertEqual(0, metrics["ambiguousOvercommitCount"])
        self.assertEqual(0.25, metrics["reviewRate"])
        self.assertEqual(25, metrics["latencyMs"])
        self.assertEqual(4096, metrics["peakMemoryBytes"])

    def test_candidate_reduction_is_unknown_without_full_pair_universe(self):
        report = evaluate_er_pipeline(
            [ERPipelineCase("match", CatalogMatchOutcome.MATCH, True, CatalogMatchOutcome.MATCH)]
        )
        self.assertIsNone(report["metrics"]["candidateReductionRatio"])
        self.assertEqual(0.0, report["metrics"]["labeledPairReductionRatio"])

    def test_filtered_review_is_counted_as_ambiguous_overcommit(self):
        report = evaluate_er_pipeline(
            [ERPipelineCase("review-filtered", CatalogMatchOutcome.REVIEW, False, None)]
        )
        self.assertEqual(1, report["metrics"]["ambiguousOvercommitCount"])

    def test_false_merge_safety_is_preserved_as_separate_metric(self):
        report = evaluate_er_pipeline(
            [ERPipelineCase("unsafe", CatalogMatchOutcome.NO_MATCH, True, CatalogMatchOutcome.MATCH)]
        )
        self.assertEqual(1, report["metrics"]["falseMergeCount"])

    def test_filtered_candidate_cannot_have_verifier_outcome(self):
        with self.assertRaisesRegex(ValueError, "filtered candidates cannot have a verifier outcome"):
            ERPipelineCase("bad", CatalogMatchOutcome.MATCH, False, CatalogMatchOutcome.MATCH)

    def test_bool_cost_values_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "latency_ms"):
            ERPipelineCost(latency_ms=True)

    def test_invalid_scale_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            ERPipelineScale(candidate_universe_size=10, retained_candidate_count=11)


if __name__ == "__main__":
    unittest.main()
