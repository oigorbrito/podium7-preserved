from pathlib import Path
import unittest

from podium7.catalog_operational import measure_source_backed_operational_corpus
from podium7.operational_disposition import plan_measured_operational_dispositions


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class MeasuredOperationalDispositionV1Tests(unittest.TestCase):
    def test_all_measured_reviews_route_to_evidence_work_without_resolver_change(self) -> None:
        measurement = measure_source_backed_operational_corpus(DATASETS)
        eligibility = measurement["provenanceEligibility"]
        plan = plan_measured_operational_dispositions(measurement)

        self.assertEqual(eligibility["records"], 60)
        self.assertEqual(eligibility["replayableRecords"], measurement["summary"]["total"])
        self.assertGreater(eligibility["blockedRecords"], 0)
        self.assertEqual(plan["assignedReviewTasks"], measurement["summary"]["review"])
        self.assertEqual(plan["resolverPolicyChanges"], 0)
        self.assertEqual(plan["unresolvedPriorities"], [])
        self.assertEqual(
            plan["assignedReviewTasks"],
            sum(action["count"] for action in plan["actions"]),
        )
        self.assertTrue(all(action["resolverPolicyChange"] is False for action in plan["actions"]))

    def test_failure_or_unknown_cause_stays_unresolved_instead_of_becoming_identity_policy(self) -> None:
        measurement = {
            "summary": {"total": 10, "review": 1, "failed": 1},
            "reviewCauses": {"UNKNOWN_REVIEW_CAUSE": 1},
        }
        plan = plan_measured_operational_dispositions(measurement)
        self.assertEqual(plan["actions"], [])
        self.assertEqual([item["gap"] for item in plan["unresolvedPriorities"]], [
            "INGESTION_FAILURES",
            "UNKNOWN_REVIEW_CAUSE",
        ])
        self.assertEqual(plan["resolverPolicyChanges"], 0)


if __name__ == "__main__":
    unittest.main()
