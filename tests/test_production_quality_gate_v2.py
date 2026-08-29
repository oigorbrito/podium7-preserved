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
        eligibility = measurement["provenanceEligibility"]
        self.assertEqual(eligibility["records"], 60)
        self.assertEqual(
            eligibility["records"],
            eligibility["replayableRecords"] + eligibility["blockedRecords"],
        )
        self.assertGreater(eligibility["blockedRecords"], 0)
        self.assertEqual(summary["total"], eligibility["replayableRecords"])
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(
            summary["created"] + summary["matched"] + summary["review"],
            summary["total"],
        )
        self.assertEqual(summary["openReviewTasks"], summary["review"])
        self.assertEqual(sum(measurement["reviewCauses"].values()), summary["review"])
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", measurement["reviewCauses"])

        metrics = quality["metrics"]
        self.assertEqual(quality["totalCases"], 30)
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedMatchCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)

        self.assertEqual(sum(item["count"] for item in priorities), summary["review"])
        self.assertTrue(all("RESOLVER" not in item["disposition"] for item in priorities))
        self.assertEqual(dispositions["assignedReviewTasks"], summary["review"])
        self.assertEqual(dispositions["unresolvedPriorities"], [])
        self.assertEqual(dispositions["resolverPolicyChanges"], 0)


if __name__ == "__main__":
    unittest.main()
