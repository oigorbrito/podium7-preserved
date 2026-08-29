from __future__ import annotations

import json
from pathlib import Path
import unittest

from podium7.expanded_corpus_measurement import measure_expanded_corpus


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "production_end_to_end_corpus_v2.json"
QUALITY_DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


class ExpandedCorpusMeasurementTests(unittest.TestCase):
    def test_integrated_corpus_and_labeled_quality_are_measured_without_conflation(self) -> None:
        measurement, artifact = measure_expanded_corpus(CORPUS, QUALITY_DATASETS)

        operational = measurement["operational"]
        summary = operational["summary"]
        self.assertEqual(summary, {"total": 8, "created": 5, "matched": 2, "review": 1, "failed": 0})
        self.assertEqual(operational["measurementScope"], "INTEGRATED_PROVENANCE_FIRST_CORPUS_V2")
        self.assertEqual(operational["explicitConflicts"]["count"], 0)
        self.assertEqual(operational["explicitConflicts"]["disposition"], "NO_EXPLICIT_CONFLICTS")

        review = operational["reviewLoad"]
        self.assertEqual(review["openReviewTasks"], 1)
        self.assertEqual(sum(review["causes"].values()), 1)
        self.assertEqual(len(review["snapshots"]), 1)
        self.assertNotIn("UNKNOWN_REVIEW_CAUSE", review["causes"])

        provenance = operational["provenance"]["summary"]
        self.assertTrue(provenance["pass"])
        self.assertEqual(provenance["incompleteLinks"], 0)
        self.assertEqual(provenance["completeness"], 1.0)
        self.assertEqual(provenance["catalogVehicles"], 5)
        self.assertEqual(provenance["openReviewTasks"], 1)

        contributions = operational["sourceContribution"]
        observed = contributions["observedInputByFieldAndSource"]
        canonical = contributions["canonicalCandidateWritesByFieldAndSource"]
        self.assertEqual(observed["make"]["vehicle-makes-models"], 2)
        self.assertEqual(observed["model"]["vehicle-makes-models"], 2)
        self.assertEqual(canonical["make"]["vehicle-makes-models"], 2)
        self.assertEqual(canonical["model"]["vehicle-makes-models"], 2)
        self.assertIn("Observed input is not a canonical write", contributions["boundary"])

        quality = measurement["labeledIdentityQuality"]
        metrics = quality["metrics"]
        self.assertEqual(quality["totalCases"], 30)
        self.assertEqual(metrics["autoMatchPrecision"], 1.0)
        self.assertEqual(metrics["autoMatchRecall"], 1.0)
        self.assertEqual(metrics["falseMergeCount"], 0)
        self.assertEqual(metrics["missedMatchCount"], 0)
        self.assertEqual(metrics["ambiguousOvercommitCount"], 0)

        boundaries = measurement["boundaries"]
        self.assertFalse(boundaries["operationalActionsAreQualityLabels"])
        self.assertFalse(boundaries["historicalV3BlockedSidesIncluded"])
        self.assertFalse(boundaries["productionCompletenessClaim"])

        self.assertEqual(artifact["operational"], operational)
        self.assertEqual(artifact["identityQuality"], quality)
        self.assertEqual(len(artifact["datasets"]), 3)

    def test_measurement_artifact_is_deterministic(self) -> None:
        first, first_artifact = measure_expanded_corpus(CORPUS, QUALITY_DATASETS)
        second, second_artifact = measure_expanded_corpus(CORPUS, QUALITY_DATASETS)
        self.assertEqual(first, second)
        self.assertEqual(first_artifact, second_artifact)
        self.assertEqual(
            json.dumps(first_artifact, sort_keys=True, separators=(",", ":")),
            json.dumps(second_artifact, sort_keys=True, separators=(",", ":")),
        )


if __name__ == "__main__":
    unittest.main()
