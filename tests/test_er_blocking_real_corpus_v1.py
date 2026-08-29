import unittest
from pathlib import Path

from podium7.catalog_benchmark import load_catalog_identity_benchmark
from podium7.er_blocking_candidates import compare_bounded_blockers


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = (
    "benchmarks/catalog_identity_golden_v1.json",
    "benchmarks/catalog_identity_golden_br_v1.json",
    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
    "benchmarks/catalog_identity_year_semantics_challenge_v1.json",
)


class ERBlockingRealCorpusV1Tests(unittest.TestCase):
    def reports(self):
        return {
            relative_path: compare_bounded_blockers(
                load_catalog_identity_benchmark(ROOT / relative_path)
            )
            for relative_path in BENCHMARKS
        }

    def test_retain_all_preserves_safety_on_retained_corpora(self):
        for path, report in self.reports().items():
            with self.subTest(path=path):
                metrics = report["candidates"]["retain-all-current-verifier"]["metrics"]
                self.assertEqual(1.0, metrics["blockingRecall"])
                self.assertEqual(1.0, metrics["endToEndMatchRecall"])
                self.assertEqual(0, metrics["falseMergeCount"])
                self.assertEqual(0, metrics["ambiguousOvercommitCount"])
                self.assertEqual(0.0, metrics["labeledPairReductionRatio"])
                self.assertIsNone(metrics["candidateReductionRatio"])

    def test_same_make_has_no_measured_labeled_pair_gain(self):
        for path, report in self.reports().items():
            with self.subTest(path=path):
                baseline = report["candidates"]["retain-all-current-verifier"]["metrics"]
                candidate = report["candidates"]["same-make"]["metrics"]
                self.assertEqual(1.0, candidate["blockingRecall"])
                self.assertEqual(0, candidate["falseMergeCount"])
                self.assertEqual(0, candidate["ambiguousOvercommitCount"])
                self.assertEqual(0.0, candidate["labeledPairReductionRatio"])
                self.assertIsNone(candidate["candidateReductionRatio"])
                for metric in (
                    "retainedLabeledPairCount",
                    "endToEndMatchPrecision",
                    "endToEndMatchRecall",
                    "reviewRate",
                ):
                    self.assertEqual(baseline[metric], candidate[metric])

    def test_same_make_model_fails_global_safety_gates(self):
        report = self.reports()["benchmarks/catalog_identity_golden_v1.json"]
        candidate = report["candidates"]["same-make-model"]
        metrics = candidate["metrics"]
        self.assertEqual(0.75, metrics["blockingRecall"])
        self.assertEqual(1, metrics["missedMatchCount"])
        self.assertEqual(2, metrics["ambiguousOvercommitCount"])
        self.assertEqual(0.25, metrics["labeledPairReductionRatio"])
        self.assertIsNone(metrics["candidateReductionRatio"])
        blocked = {
            case["caseId"]
            for case in candidate["cases"]
            if not case["candidateRetained"]
        }
        self.assertEqual(
            {
                "match-bmw-g20-330e-alias",
                "review-porsche-911-partial-variant-label",
                "review-bmw-g20-generic-vs-330i-label",
            },
            blocked,
        )

    def test_same_make_model_fails_brazil_blocking_recall(self):
        report = self.reports()["benchmarks/catalog_identity_golden_br_v1.json"]
        candidate = report["candidates"]["same-make-model"]
        metrics = candidate["metrics"]
        self.assertEqual(0.5, metrics["blockingRecall"])
        self.assertEqual(2, metrics["missedMatchCount"])
        self.assertEqual(0, metrics["ambiguousOvercommitCount"])
        self.assertAlmostEqual(1 / 6, metrics["labeledPairReductionRatio"])
        self.assertIsNone(metrics["candidateReductionRatio"])
        blocked_matches = {
            case["caseId"]
            for case in candidate["cases"]
            if case["expected"] == "MATCH" and not case["candidateRetained"]
        }
        self.assertEqual(
            {
                "br-match-corolla-cross-xrx-hybrid-my25",
                "br-match-tcross-highline-250-tsi",
            },
            blocked_matches,
        )

    def test_same_make_model_has_no_gain_on_remaining_challenge_slices(self):
        reports = self.reports()
        for path in (
            "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
            "benchmarks/catalog_identity_year_semantics_challenge_v1.json",
        ):
            with self.subTest(path=path):
                metrics = reports[path]["candidates"]["same-make-model"]["metrics"]
                self.assertEqual(1.0, metrics["blockingRecall"])
                self.assertEqual(0, metrics["falseMergeCount"])
                self.assertEqual(0, metrics["ambiguousOvercommitCount"])
                self.assertEqual(0.0, metrics["labeledPairReductionRatio"])
                self.assertIsNone(metrics["candidateReductionRatio"])


if __name__ == "__main__":
    unittest.main()
