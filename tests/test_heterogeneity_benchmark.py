import math
import unittest

from podium7.heterogeneity_benchmark import evaluate_heterogeneity_slices


class HeterogeneityBenchmarkTests(unittest.TestCase):
    def baseline(self):
        return {
            "autoMatchPrecision": 1.0,
            "autoMatchRecall": 0.9,
            "falseMergeCount": 0,
            "missedMatchCount": 1,
            "ambiguousOvercommitCount": 0,
            "reviewRate": 0.2,
        }

    def test_reports_deltas_without_redefining_podium_metrics(self):
        report = evaluate_heterogeneity_slices(
            self.baseline(),
            {
                "schema-mismatch": {
                    "autoMatchPrecision": 1.0,
                    "autoMatchRecall": 0.7,
                    "falseMergeCount": 0,
                    "missedMatchCount": 3,
                    "ambiguousOvercommitCount": 0,
                    "reviewRate": 0.4,
                }
            },
        )
        item = report["slices"][0]
        self.assertAlmostEqual(-0.2, item["deltas"]["recallDelta"])
        self.assertEqual(2.0, item["deltas"]["missedMatchDelta"])
        self.assertAlmostEqual(0.2, item["deltas"]["reviewRateDelta"])
        self.assertFalse(item["safetyRegression"])

    def test_false_merge_regression_is_flagged(self):
        metrics = self.baseline()
        metrics["falseMergeCount"] = 1
        report = evaluate_heterogeneity_slices(self.baseline(), {"semantic": metrics})
        self.assertTrue(report["slices"][0]["safetyRegression"])
        self.assertEqual(1, report["safetyRegressionSliceCount"])

    def test_ambiguous_overcommit_regression_is_flagged(self):
        metrics = self.baseline()
        metrics["ambiguousOvercommitCount"] = 1
        report = evaluate_heterogeneity_slices(self.baseline(), {"granularity": metrics})
        self.assertTrue(report["slices"][0]["safetyRegression"])

    def test_rate_outside_unit_interval_fails_closed(self):
        metrics = self.baseline()
        metrics["reviewRate"] = 1.1
        with self.assertRaisesRegex(ValueError, "reviewRate must be between 0 and 1"):
            evaluate_heterogeneity_slices(self.baseline(), {"invalid": metrics})

    def test_non_finite_rate_fails_closed(self):
        for value in (math.nan, math.inf, -math.inf):
            metrics = self.baseline()
            metrics["autoMatchRecall"] = value
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "autoMatchRecall must be finite"):
                    evaluate_heterogeneity_slices(self.baseline(), {"invalid": metrics})

    def test_bool_count_fails_closed(self):
        metrics = self.baseline()
        metrics["falseMergeCount"] = True
        with self.assertRaisesRegex(ValueError, "falseMergeCount"):
            evaluate_heterogeneity_slices(self.baseline(), {"invalid": metrics})


if __name__ == "__main__":
    unittest.main()
