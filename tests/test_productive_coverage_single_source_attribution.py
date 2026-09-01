import unittest
from pathlib import Path

from podium7.catalog_benchmark import load_catalog_identity_benchmark
from podium7.operational_provenance import (
    BLOCK_MISSING_SIDE_FIELD_ATTRIBUTION,
    BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION,
    measure_operational_provenance_eligibility,
)


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_DATASET = ROOT / "benchmarks" / "catalog_identity_golden_v1.json"
BR_DATASET = ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json"
BR_ADJACENT_DATASET = ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json"
WAVE_DATASETS = (GLOBAL_DATASET, BR_DATASET, BR_ADJACENT_DATASET)

EXPECTED_EXPLICIT = {
    ("match-porsche-911-992-carrera-4s", "left"): "porsche-911-generations-2019",
    ("match-porsche-911-992-carrera-4s", "right"): "porsche-911-generations-2019",
    ("no-match-toyota-corolla-10g-vs-12g", "right"): "toyota-corolla-2018-global",
    ("no-match-porsche-911-991-vs-992", "right"): "porsche-911-generations-2019",
    ("review-porsche-911-partial-variant-label", "left"): "porsche-911-992-powertrain-2019",
    ("review-porsche-911-partial-variant-label", "right"): "porsche-911-992-powertrain-2019",
    ("br-hard-no-match-corolla-altis-hybrid-my25-vs-my26", "left"): "toyota-connected-services-corolla-my25",
    ("br-hard-no-match-corolla-altis-hybrid-my25-vs-my26", "right"): "toyota-corolla-altis-hybrid-offer-2026",
    ("br-hard-no-match-onix-premier-my26-vs-my27", "left"): "chevrolet-onix-my26-price-list",
    ("br-hard-no-match-onix-premier-my26-vs-my27", "right"): "chevrolet-onix-line-2027",
}

EXPECTED_INSUFFICIENT = {
    ("no-match-toyota-corolla-10g-vs-12g", "left"),
    ("no-match-porsche-911-991-vs-992", "left"),
}


class ProductiveCoverageSingleSourceAttributionTests(unittest.TestCase):
    def test_changed_benchmarks_remain_valid_catalog_benchmarks(self) -> None:
        global_dataset = load_catalog_identity_benchmark(GLOBAL_DATASET)
        adjacent_dataset = load_catalog_identity_benchmark(BR_ADJACENT_DATASET)

        self.assertEqual(len(global_dataset.cases), 12)
        self.assertEqual(len(adjacent_dataset.cases), 6)

    def test_verified_attribution_produces_exact_frozen_wave_delta(self) -> None:
        report = measure_operational_provenance_eligibility(WAVE_DATASETS)
        summary = report["summary"]

        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 22)
        self.assertEqual(summary["blockedRecords"], 38)
        self.assertEqual(summary["replayableRate"], 22 / 60)
        self.assertEqual(
            summary["replayableByMethod"],
            {"EXPLICIT_FIELD_ATTRIBUTION": 10, "SOLE_CASE_SOURCE": 12},
        )
        self.assertEqual(
            summary["blockedByReasonCode"],
            {
                BLOCK_MISSING_SIDE_FIELD_ATTRIBUTION: 2,
                BLOCK_MULTI_SOURCE_WITHOUT_FIELD_ATTRIBUTION: 36,
            },
        )

    def test_only_verified_sides_become_explicitly_replayable(self) -> None:
        report = measure_operational_provenance_eligibility(WAVE_DATASETS)
        explicit = {
            (record["caseId"], record["side"]): record["sourceId"]
            for record in report["records"]
            if record["method"] == "EXPLICIT_FIELD_ATTRIBUTION"
        }
        self.assertEqual(explicit, EXPECTED_EXPLICIT)

    def test_two_insufficient_sides_remain_fail_closed(self) -> None:
        report = measure_operational_provenance_eligibility(WAVE_DATASETS)
        missing_side = {
            (record["caseId"], record["side"])
            for record in report["records"]
            if record["reasonCode"] == BLOCK_MISSING_SIDE_FIELD_ATTRIBUTION
        }
        self.assertEqual(missing_side, EXPECTED_INSUFFICIENT)


if __name__ == "__main__":
    unittest.main()
