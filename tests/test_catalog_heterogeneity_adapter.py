import math
import unittest
from unittest.mock import patch

from podium7.catalog import CatalogMatchOutcome, CatalogVehicleIdentity
from podium7.catalog_benchmark import CatalogBenchmarkCase, CatalogBenchmarkDataset
from podium7.catalog_heterogeneity_adapter import (
    compare_catalog_heterogeneity,
    podium_safety_metrics_from_catalog_report,
)


class CatalogHeterogeneityAdapterTests(unittest.TestCase):
    def report(self, *, precision=1.0, recall=1.0, false_merges=0, missed=0, overcommit=0, review=0.0):
        return {
            "metrics": {
                "matchPrecision": precision,
                "matchRecall": recall,
                "falseMergeCount": false_merges,
                "missedDuplicateCount": missed,
                "ambiguousOvercommitCount": overcommit,
                "reviewRate": review,
            }
        }

    def case(self, case_id="same", expected=CatalogMatchOutcome.MATCH):
        return CatalogBenchmarkCase(
            id=case_id,
            expected=expected,
            left=CatalogVehicleIdentity(make="Ford", model="Mustang"),
            right=CatalogVehicleIdentity(make="Ford", model="Mustang"),
            source_ids=("s",),
            rationale="test",
        )

    def test_maps_existing_catalog_metrics_without_redefinition(self):
        metrics = podium_safety_metrics_from_catalog_report(self.report(recall=0.8, missed=2))
        self.assertEqual(0.8, metrics["autoMatchRecall"])
        self.assertEqual(2, metrics["missedMatchCount"])
        self.assertEqual(0, metrics["falseMergeCount"])

    def test_compare_wires_clean_and_heterogeneous_reports_into_delta_contract(self):
        clean = CatalogBenchmarkDataset(version="clean", source_ids=("s",), cases=(self.case(),))
        heterogeneous = CatalogBenchmarkDataset(version="heterogeneous", source_ids=("s",), cases=(self.case(),))
        with patch(
            "podium7.catalog_heterogeneity_adapter.evaluate_catalog_identity_benchmark",
            side_effect=[
                self.report(recall=1.0, missed=0),
                self.report(recall=0.5, missed=1, review=0.5),
            ],
        ):
            report = compare_catalog_heterogeneity(clean, {"schema-mismatch": heterogeneous})
        item = report["slices"][0]
        self.assertEqual(-0.5, item["deltas"]["recallDelta"])
        self.assertEqual(1.0, item["deltas"]["missedMatchDelta"])
        self.assertFalse(item["safetyRegression"])
        self.assertEqual("clean", report["cleanDatasetVersion"])
        self.assertEqual("heterogeneous", report["sliceDatasetVersions"]["schema-mismatch"])

    def test_slice_must_preserve_case_ids_and_gold_labels(self):
        clean = CatalogBenchmarkDataset(version="clean", source_ids=("s",), cases=(self.case(),))
        changed = CatalogBenchmarkDataset(
            version="changed",
            source_ids=("s",),
            cases=(self.case(case_id="different", expected=CatalogMatchOutcome.NO_MATCH),),
        )
        with self.assertRaisesRegex(ValueError, "preserve the clean case ids and expected labels"):
            compare_catalog_heterogeneity(clean, {"invalid": changed})

    def test_missing_catalog_metric_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing metrics"):
            podium_safety_metrics_from_catalog_report({"metrics": {}})

    def test_malformed_catalog_metric_fails_at_adapter_boundary(self):
        for field, value, pattern in (
            ("recall", math.nan, "autoMatchRecall must be finite"),
            ("review", 1.1, "reviewRate must be between 0 and 1"),
            ("false_merges", True, "falseMergeCount must be a non-negative integer"),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaisesRegex(ValueError, pattern):
                    podium_safety_metrics_from_catalog_report(self.report(**{field: value}))

    def test_non_mapping_catalog_report_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "report must be an object"):
            podium_safety_metrics_from_catalog_report([])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
