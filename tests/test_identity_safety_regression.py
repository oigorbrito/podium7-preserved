import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog_quality import evaluate_identity_quality
from podium7.identity_regression import (
    compare_identity_quality_to_baseline,
    load_identity_safety_baseline,
)


ROOT = Path(__file__).resolve().parents[1]
RETAINED = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
BASELINE = ROOT / "benchmarks" / "production_identity_safety_baseline_v3.json"


class IdentitySafetyRegressionTests(unittest.TestCase):
    def test_retained_quality_matches_documented_v3_baseline(self) -> None:
        quality = evaluate_identity_quality(RETAINED)
        baseline = load_identity_safety_baseline(BASELINE)
        report = compare_identity_quality_to_baseline(quality, baseline)
        self.assertTrue(report["passed"])
        self.assertEqual([], report["regressions"])
        self.assertEqual(30, report["totalCases"])
        self.assertTrue(all(item["passed"] for item in report["metrics"].values()))

    def test_regression_is_reported_without_changing_thresholds(self) -> None:
        baseline = load_identity_safety_baseline(BASELINE)
        quality = {
            "datasets": list(baseline["datasets"]),
            "totalCases": baseline["totalCases"],
            "metrics": {
                "autoMatchPrecision": 0.95,
                "autoMatchRecall": 0.90,
                "falseMergeCount": 1,
                "ambiguousOvercommitCount": 1,
            },
        }
        report = compare_identity_quality_to_baseline(quality, baseline)
        self.assertFalse(report["passed"])
        self.assertEqual(
            ["autoMatchPrecision", "autoMatchRecall", "falseMergeCount", "ambiguousOvercommitCount"],
            report["regressions"],
        )

    def test_dataset_contract_mismatch_fails_closed(self) -> None:
        baseline = load_identity_safety_baseline(BASELINE)
        quality = {
            "datasets": ["wrong"],
            "totalCases": baseline["totalCases"],
            "metrics": dict(baseline["metrics"]),
        }
        with self.assertRaisesRegex(ValueError, "dataset contract mismatch"):
            compare_identity_quality_to_baseline(quality, baseline)

    def test_case_count_contract_mismatch_fails_closed(self) -> None:
        baseline = load_identity_safety_baseline(BASELINE)
        quality = {
            "datasets": list(baseline["datasets"]),
            "totalCases": 29,
            "metrics": dict(baseline["metrics"]),
        }
        with self.assertRaisesRegex(ValueError, "case-count contract mismatch"):
            compare_identity_quality_to_baseline(quality, baseline)

    def test_boolean_or_out_of_range_metrics_fail_closed(self) -> None:
        baseline = load_identity_safety_baseline(BASELINE)
        for metric, value in (
            ("autoMatchPrecision", True),
            ("autoMatchRecall", 1.01),
            ("falseMergeCount", False),
            ("ambiguousOvercommitCount", -1),
        ):
            with self.subTest(metric=metric, value=value):
                quality = {
                    "datasets": list(baseline["datasets"]),
                    "totalCases": baseline["totalCases"],
                    "metrics": {**baseline["metrics"], metric: value},
                }
                with self.assertRaisesRegex(ValueError, metric):
                    compare_identity_quality_to_baseline(quality, baseline)

    def test_malformed_baseline_metric_fails_closed_on_load(self) -> None:
        payload = json.loads(BASELINE.read_text(encoding="utf-8"))
        payload["metrics"]["autoMatchPrecision"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-baseline.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "autoMatchPrecision"):
                load_identity_safety_baseline(path)


if __name__ == "__main__":
    unittest.main()
