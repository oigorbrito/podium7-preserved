from pathlib import Path
import unittest
from unittest.mock import patch

from podium7.catalog_quality import evaluate_identity_quality


class IdentityQualityMetricSemanticsTests(unittest.TestCase):
    def test_ambiguous_overcommit_is_not_double_counted_as_false_merge(self) -> None:
        benchmark_report = {
            "datasetVersion": "metric-separation-v1",
            "cases": [
                {
                    "id": "ambiguous-overcommit",
                    "expected": "REVIEW",
                    "predicted": "MATCH",
                    "reason": "controlled metric-semantics report",
                }
            ],
        }
        with (
            patch("podium7.catalog_quality.load_catalog_identity_benchmark", return_value=object()),
            patch("podium7.catalog_quality.evaluate_catalog_identity_benchmark", return_value=benchmark_report),
        ):
            metrics = evaluate_identity_quality((Path("controlled.json"),))["metrics"]

        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 1)
        self.assertEqual(metrics["reviewRate"], 0.0)


if __name__ == "__main__":
    unittest.main()
