from pathlib import Path
import unittest

from podium7.catalog_operational import measure_source_backed_operational_corpus
from podium7.operational_priority import prioritize_operational_gaps


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ProductionOperationalGapPriorityV1Tests(unittest.TestCase):
    def test_measured_gap_priority_is_evidence_enrichment_not_resolver_weakening(self) -> None:
        priorities = prioritize_operational_gaps(
            measure_source_backed_operational_corpus(DATASETS)
        )

        self.assertEqual([item["gap"] for item in priorities], [
            "MISSING_IDENTITY_EVIDENCE",
            "LABEL_AMBIGUITY",
        ])
        self.assertEqual(priorities[0]["count"], 3)
        self.assertEqual(priorities[0]["disposition"], "ENRICH_IDENTITY_EVIDENCE")
        self.assertAlmostEqual(priorities[0]["reviewShare"], 3 / 4)
        self.assertEqual(priorities[1]["count"], 1)
        self.assertEqual(priorities[1]["disposition"], "ENRICH_LABEL_EVIDENCE")
        self.assertTrue(all("RESOLVER" not in item["disposition"] for item in priorities))

    def test_failures_and_unknown_review_causes_preempt_known_review_friction(self) -> None:
        measurement = {
            "summary": {"total": 10, "review": 4, "failed": 2},
            "reviewCauses": {"MISSING_IDENTITY_EVIDENCE": 3, "UNKNOWN_REVIEW_CAUSE": 1},
        }
        priorities = prioritize_operational_gaps(measurement)
        self.assertEqual(priorities[0]["gap"], "INGESTION_FAILURES")
        self.assertEqual(priorities[1]["gap"], "UNKNOWN_REVIEW_CAUSE")


if __name__ == "__main__":
    unittest.main()
