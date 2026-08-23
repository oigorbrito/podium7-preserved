from __future__ import annotations

import json
from pathlib import Path
import unittest

from podium7.source_distribution import SourceSlice, evaluate_source_distribution


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks" / "production_source_distribution_v1.json"


class SourceDistributionTests(unittest.TestCase):
    def test_benchmark_passes_bounded_distribution_contract(self) -> None:
        payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        slices = tuple(
            SourceSlice(
                source_family=item["sourceFamily"],
                region=item["region"],
                records=item["records"],
                independently_inspected=item["independentlyInspected"],
            )
            for item in payload["slices"]
        )
        self.assertEqual(payload["expected"], evaluate_source_distribution(slices))

    def test_uninspected_slice_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "uninspected"):
            evaluate_source_distribution((SourceSlice("x", "US", 1, False),))

    def test_insufficient_geographic_or_source_diversity_does_not_pass(self) -> None:
        report = evaluate_source_distribution((
            SourceSlice("a", "US", 5),
            SourceSlice("b", "US", 5),
            SourceSlice("c", "US", 5),
        ))
        self.assertFalse(report["passed"])

    def test_single_family_dominance_does_not_pass(self) -> None:
        report = evaluate_source_distribution((
            SourceSlice("a", "US", 80),
            SourceSlice("b", "EU", 10),
            SourceSlice("c", "BR", 10),
        ))
        self.assertFalse(report["passed"])


if __name__ == "__main__":
    unittest.main()
