import unittest
from pathlib import Path

from podium7.catalog_benchmark import load_catalog_identity_benchmark
from podium7.catalog_resolution_precedence import (
    resolve_catalog_pair_with_structural_precedence,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class CatalogOperationalResolverBenchmarkTests(unittest.TestCase):
    def test_operational_resolver_preserves_all_curated_benchmark_labels(self) -> None:
        for path in DATASETS:
            dataset = load_catalog_identity_benchmark(path)
            for case in dataset.cases:
                with self.subTest(dataset=dataset.version, case=case.id):
                    decision = resolve_catalog_pair_with_structural_precedence(
                        case.left,
                        case.right,
                    )
                    self.assertIs(decision.outcome, case.expected)


if __name__ == "__main__":
    unittest.main()
