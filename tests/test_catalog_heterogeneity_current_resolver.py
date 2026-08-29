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

    def assert_expected_match_degradation(self, item, *, review_delta, missed_delta=1.0):
        self.assertEqual(-1.0, item["deltas"]["recallDelta"])
        self.assertEqual(missed_delta, item["deltas"]["missedMatchDelta"])
        self.assertEqual(0.0, item["deltas"]["falseMergeDelta"])
        self.assertEqual(0.0, item["deltas"]["ambiguousOvercommitDelta"])
        self.assertEqual(review_delta, item["deltas"]["reviewRateDelta"])
        self.assertFalse(item["safetyRegression"])

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

    def test_nomenclature_hyphen_compaction_is_measured(self):
        left = CatalogVehicleIdentity(
            make="Mazda",
            model="CX-5",
            generation="KF",
            powertrain="2.5 Skyactiv-G",
            transmission="AT-6",
            body_style="SUV",
            market="US",
        )
        clean_right = CatalogVehicleIdentity(
            make="MAZDA",
            model="CX-5",
            generation="kf",
            powertrain="Skyactiv-G 2.5",
            transmission="AT-6",
            body_style="suv",
            market="us",
        )
        heterogeneous_right = CatalogVehicleIdentity(
            make="MAZDA",
            model="CX5",
            generation="kf",
            powertrain="Skyactiv-G 2.5",
            transmission="AT-6",
            body_style="suv",
            market="us",
        )
        report = compare_catalog_heterogeneity(
            self.dataset("clean-nomenclature", clean_right, left_identity=left),
            {
                "nomenclature-hyphen-compaction": self.dataset(
                    "heterogeneous-nomenclature", heterogeneous_right, left_identity=left
                )
            },
        )
        self.assert_expected_match_degradation(report["slices"][0], review_delta=0.0)

    def test_structural_missing_trim_field_is_measured_as_review(self):
        left = CatalogVehicleIdentity(
            make="Toyota",
            model="Corolla",
            generation="E210",
            variant="XSE",
            powertrain="2.0 Dynamic Force",
            transmission="CVT",
            body_style="Sedan",
            market="US",
        )
        clean_right = CatalogVehicleIdentity(
            make="TOYOTA",
            model="COROLLA",
            generation="e210",
            variant="xse",
            powertrain="Dynamic Force 2.0",
            transmission="cvt",
            body_style="sedan",
            market="us",
        )
        heterogeneous_right = CatalogVehicleIdentity(
            make="TOYOTA",
            model="COROLLA",
            generation="e210",
            variant="xse",
            powertrain="Dynamic Force 2.0",
            transmission="cvt",
            body_style=None,
            market="us",
        )
        report = compare_catalog_heterogeneity(
            self.dataset("clean-structural", clean_right, left_identity=left),
            {
                "structural-missing-body-style": self.dataset(
                    "heterogeneous-structural", heterogeneous_right, left_identity=left
                )
            },
        )
        self.assert_expected_match_degradation(
            report["slices"][0], review_delta=1.0, missed_delta=0.0
        )

    def test_unit_heterogeneity_is_measured_without_unit_conversion_inference(self):
        left = CatalogVehicleIdentity(
            make="Polestar",
            model="2",
            generation="1",
            powertrain="150 kW",
            transmission="1-speed",
            body_style="Fastback",
            market="EU",
        )
        clean_right = CatalogVehicleIdentity(
            make="POLESTAR",
            model="2",
            generation="1",
            powertrain="150 kW",
            transmission="1-speed",
            body_style="fastback",
            market="eu",
        )
        heterogeneous_right = CatalogVehicleIdentity(
            make="POLESTAR",
            model="2",
            generation="1",
            powertrain="201 hp",
            transmission="1-speed",
            body_style="fastback",
            market="eu",
        )
        report = compare_catalog_heterogeneity(
            self.dataset("clean-unit", clean_right, left_identity=left),
            {"unit-power-output": self.dataset("heterogeneous-unit", heterogeneous_right, left_identity=left)},
        )
        self.assert_expected_match_degradation(report["slices"][0], review_delta=0.0)

    def test_granularity_mismatch_is_measured_as_review(self):
        left = CatalogVehicleIdentity(
            make="Toyota",
            model="RAV4 Prime",
            generation="XA50",
            powertrain="PHEV",
            transmission="eCVT",
            body_style="SUV",
            market="US",
        )
        clean_right = CatalogVehicleIdentity(
            make="TOYOTA",
            model="RAV4 PRIME",
            generation="xa50",
            powertrain="phev",
            transmission="ecvt",
            body_style="suv",
            market="us",
        )
        heterogeneous_right = CatalogVehicleIdentity(
            make="TOYOTA",
            model="RAV4",
            generation="xa50",
            powertrain="phev",
            transmission="ecvt",
            body_style="suv",
            market="us",
        )
        report = compare_catalog_heterogeneity(
            self.dataset("clean-granularity", clean_right, left_identity=left),
            {
                "granularity-model-family": self.dataset(
                    "heterogeneous-granularity", heterogeneous_right, left_identity=left
                )
            },
        )
        self.assert_expected_match_degradation(
            report["slices"][0], review_delta=1.0, missed_delta=0.0
        )

    def test_combined_representation_and_structural_heterogeneity_is_measured(self):
        left = CatalogVehicleIdentity(
            make="Ford",
            model="Mustang Mach-E",
            generation="1",
            variant="Premium",
            powertrain="BEV AWD",
            transmission="1-speed",
            body_style="SUV",
            market="US",
        )
        clean_right = CatalogVehicleIdentity(
            make="FORD",
            model="MUSTANG MACH E",
            generation="1",
            variant="premium",
            powertrain="AWD BEV",
            transmission="1-speed",
            body_style="suv",
            market="us",
        )
        heterogeneous_right = CatalogVehicleIdentity(
            make="FORD",
            model="MUSTANG MACH E",
            generation="1",
            variant="premium",
            powertrain="AWD BEV",
            transmission="1speed",
            body_style=None,
            market="us",
        )
        report = compare_catalog_heterogeneity(
            self.dataset("clean-combined", clean_right, left_identity=left),
            {
                "combined-representation-structural": self.dataset(
                    "heterogeneous-combined", heterogeneous_right, left_identity=left
                )
            },
        )
        self.assert_expected_match_degradation(report["slices"][0], review_delta=0.0)


if __name__ == "__main__":
    unittest.main()
