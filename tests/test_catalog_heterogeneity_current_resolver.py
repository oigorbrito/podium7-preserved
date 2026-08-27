import unittest

from podium7.catalog import CatalogMatchOutcome, CatalogVehicleIdentity
from podium7.catalog_benchmark import CatalogBenchmarkCase, CatalogBenchmarkDataset
from podium7.catalog_heterogeneity_adapter import compare_catalog_heterogeneity


class CurrentResolverHeterogeneityTests(unittest.TestCase):
    def dataset(self, version, right_identity, *, expected=CatalogMatchOutcome.MATCH, left_identity=None):
        left = left_identity or CatalogVehicleIdentity(
            make="Ford",
            model="Mustang",
            generation="S650",
            variant="Dark Horse",
            powertrain="5.0 V8",
            transmission="M-6",
            body_style="Coupe",
            market="US",
        )
        return CatalogBenchmarkDataset(
            version=version,
            source_ids=("stress-fixture",),
            cases=(
                CatalogBenchmarkCase(
                    id="paired-case",
                    expected=expected,
                    left=left,
                    right=right_identity,
                    source_ids=("stress-fixture",),
                    rationale="controlled heterogeneity stress fixture",
                ),
            ),
        )

    def test_representation_heterogeneity_degrades_recall_without_false_merge(self):
        clean_right = CatalogVehicleIdentity(
            make="FORD",
            model="MUSTANG",
            generation="s650",
            variant="dark horse",
            powertrain="V8 5.0",
            transmission="M-6",
            body_style="coupe",
            market="us",
        )
        heterogeneous_right = CatalogVehicleIdentity(
            make="FORD",
            model="MUSTANG",
            generation="s650",
            variant="dark horse",
            powertrain="V8 5.0",
            transmission="M6",
            body_style="coupe",
            market="us",
        )
        report = compare_catalog_heterogeneity(
            self.dataset("clean", clean_right),
            {"representation-transmission": self.dataset("heterogeneous", heterogeneous_right)},
        )
        item = report["slices"][0]
        self.assertEqual(-1.0, item["deltas"]["recallDelta"])
        self.assertEqual(1.0, item["deltas"]["missedMatchDelta"])
        self.assertEqual(0.0, item["deltas"]["falseMergeDelta"])
        self.assertFalse(item["safetyRegression"])

    def test_semantic_misprojection_into_retail_variant_is_detected_as_overcommit(self):
        left = CatalogVehicleIdentity(
            make="Volkswagen",
            model="Golf",
            generation="8",
            variant="Highline",
            powertrain="1.5 TSI",
            transmission="DCT-7",
            body_style="Hatchback",
            market="EU",
            model_year_from=2026,
            model_year_to=2026,
        )
        clean_right = CatalogVehicleIdentity(
            make="Volkswagen",
            model="Golf",
            generation="8",
            variant="Highline",
            powertrain="1.5 TSI",
            transmission="DCT-7",
            body_style="Hatchback",
            market="EU",
        )
        bad_semantic_projection = CatalogVehicleIdentity(
            make="Volkswagen",
            model="Golf",
            generation="8",
            variant="TYPE-VARIANT-VERSION-X",
            powertrain="1.5 TSI",
            transmission="DCT-7",
            body_style="Hatchback",
            market="EU",
        )
        clean = self.dataset(
            "clean-semantic",
            clean_right,
            expected=CatalogMatchOutcome.REVIEW,
            left_identity=left,
        )
        heterogeneous = self.dataset(
            "bad-regulatory-projection",
            bad_semantic_projection,
            expected=CatalogMatchOutcome.REVIEW,
            left_identity=left,
        )
        report = compare_catalog_heterogeneity(clean, {"regulatory-to-retail-variant": heterogeneous})
        item = report["slices"][0]
        self.assertEqual(1.0, item["deltas"]["ambiguousOvercommitDelta"])
        self.assertTrue(item["safetyRegression"])


if __name__ == "__main__":
    unittest.main()
