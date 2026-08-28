from pathlib import Path
import unittest

from podium7.catalog_operational import measure_source_backed_operational_corpus
from podium7.catalog_quality import evaluate_identity_quality
from podium7.operational_disposition import plan_measured_operational_dispositions
from podium7.operational_priority import prioritize_operational_gaps


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionQualityGateV2Tests(unittest.TestCase):
    def test_bounded_product_operation_cycle_passes_integrated_quality_gate(self) -> None:
        measurement = measure_source_backed_operational_corpus(DATASETS)
        quality = evaluate_identity_quality(DATASETS)
        priorities = prioritize_operational_gaps(measurement)
        dispositions = plan_measured_operational_dispositions(measurement)

        summary = measurement["summary"]
        self.assertEqual(summary["total"], 12)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["created"], 4)
        self.assertEqual(summary["matched"], 4)
        self.assertEqual(summary["review"], 4)
        self.assertEqual(summary["openReviewTasks"], 4)
        self.assertEqual(measurement["reviewCauses"], {
            "LABEL_AMBIGUITY": 1,
            "MISSING_IDENTITY_EVIDENCE": 3,
        })

        metrics = quality["metrics"]
        self.assertEqual(quality["totalCases"], 30)
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedMatchCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)

        self.assertEqual(priorities[0]["gap"], "MISSING_IDENTITY_EVIDENCE")
        self.assertEqual(priorities[0]["count"], 3)
        self.assertEqual(dispositions["assignedReviewTasks"], 4)
        self.assertEqual(dispositions["unresolvedPriorities"], [])
        self.assertEqual(dispositions["resolverPolicyChanges"], 0)


if __name__ == "__main__":
    unittest.main()
