import unittest

from podium7.catalog import CatalogMatchOutcome, CatalogVehicleIdentity
from podium7.catalog_benchmark import CatalogBenchmarkCase, CatalogBenchmarkDataset
from podium7.er_blocking_candidates import compare_bounded_blockers


class ERBlockingCandidateTests(unittest.TestCase):
    def dataset(self):
        return CatalogBenchmarkDataset(
            version="test",
            source_ids=("s1",),
            cases=(
                CatalogBenchmarkCase(
                    id="same",
                    expected=CatalogMatchOutcome.MATCH,
                    left=CatalogVehicleIdentity(make="Ford", model="Mustang"),
                    right=CatalogVehicleIdentity(make="Ford", model="Mustang"),
                    source_ids=("s1",),
                    rationale="same make/model",
                ),
                CatalogBenchmarkCase(
                    id="different-model",
                    expected=CatalogMatchOutcome.NO_MATCH,
                    left=CatalogVehicleIdentity(make="Ford", model="Mustang"),
                    right=CatalogVehicleIdentity(make="Ford", model="Focus"),
                    source_ids=("s1",),
                    rationale="different model",
                ),
                CatalogBenchmarkCase(
                    id="different-make",
                    expected=CatalogMatchOutcome.NO_MATCH,
                    left=CatalogVehicleIdentity(make="Ford", model="Mustang"),
                    right=CatalogVehicleIdentity(make="Toyota", model="Mustang"),
                    source_ids=("s1",),
                    rationale="different make",
                ),
            ),
        )

    def test_same_make_model_reduces_candidates_without_dropping_gold_match(self):
        report = compare_bounded_blockers(self.dataset())
        baseline = report["candidates"]["retain-all-current-verifier"]["metrics"]
        strict = report["candidates"]["same-make-model"]["metrics"]
        self.assertEqual(0.0, baseline["candidateReductionRatio"])
        self.assertGreater(strict["candidateReductionRatio"], 0.0)
        self.assertEqual(1.0, strict["blockingRecall"])
        self.assertEqual(0, strict["falseMergeCount"])
        self.assertEqual(0, strict["ambiguousOvercommitCount"])

    def test_comparison_keeps_current_verifier_constant(self):
        report = compare_bounded_blockers(self.dataset())
        for candidate in report["candidates"].values():
            self.assertIn("endToEndMatchPrecision", candidate["metrics"])
            self.assertIn("endToEndMatchRecall", candidate["metrics"])


if __name__ == "__main__":
    unittest.main()
