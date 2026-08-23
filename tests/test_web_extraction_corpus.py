import unittest
from collections import Counter
from pathlib import Path

from podium7.web_extraction_benchmark import (
    evaluate_web_extraction_bounded_corpus,
    evaluate_web_extraction_bounded_partial_evidence_corpus,
    evaluate_web_extraction_corpus,
    evaluate_web_extraction_partial_evidence_corpus,
    load_web_extraction_bounded_gold,
    load_web_extraction_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "benchmarks" / "web_extraction_source_family_corpus_v1.json"
BOUNDED_GOLD = ROOT / "benchmarks" / "web_extraction_bounded_values_v1.json"


class WebExtractionSourceFamilyCorpusTests(unittest.TestCase):
    def test_corpus_is_frozen_diverse_and_source_backed(self) -> None:
        dataset = load_web_extraction_corpus(DATASET)

        self.assertEqual(dataset.version, "autoevolution-source-family-1.0")
        self.assertEqual(dataset.artifact, "AUTOEVOLUTION_ARTEGA_GT_RULES")
        self.assertEqual(len(dataset.cases), 12)
        self.assertEqual(len({case.manufacturer for case in dataset.cases}), 7)
        self.assertGreaterEqual(len({case.source_url for case in dataset.cases}), 8)
        self.assertEqual(
            Counter(case.expected_outcome for case in dataset.cases),
            Counter({"SUCCESS": 8, "FAIL": 4}),
        )
        self.assertEqual(sum(case.source_target_field_count for case in dataset.cases), 142)
        self.assertTrue(all(case.snapshot_path.is_file() for case in dataset.cases))
        self.assertTrue(all(case.source_url.startswith("https://www.autoevolution.com/") for case in dataset.cases))

    def test_existing_artifact_has_reproducible_source_family_characterization(self) -> None:
        dataset = load_web_extraction_corpus(DATASET)
        report = evaluate_web_extraction_corpus(dataset)
        metrics = report["metrics"]
        by_id = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["artifact"], "AUTOEVOLUTION_ARTEGA_GT_RULES")
        self.assertEqual(report["datasetVersion"], "autoevolution-source-family-1.0")
        self.assertEqual(report["totalCases"], 12)
        self.assertEqual(metrics["pageSuccessCount"], 8)
        self.assertEqual(metrics["pageSuccessRate"], 8 / 12)
        self.assertEqual(metrics["explicitFailureCount"], 4)
        self.assertEqual(metrics["explicitFailureRate"], 4 / 12)
        self.assertEqual(metrics["expectedOutcomeMatches"], 12)
        self.assertEqual(metrics["expectedOutcomeMatchRate"], 1.0)
        self.assertEqual(metrics["fullyCorrectPageCount"], 8)
        self.assertEqual(metrics["targetFieldCount"], 142)
        self.assertEqual(metrics["emittedFieldCount"], 96)
        self.assertEqual(metrics["correctFieldCount"], 96)
        self.assertEqual(metrics["fieldPrecision"], 1.0)
        self.assertEqual(metrics["fieldRecall"], 96 / 142)
        self.assertTrue(all(not case["incorrectFields"] for case in report["cases"]))

        self.assertIn(
            "required web field 'Unladen Weight' is missing",
            by_id["bmw-g20-320i-rwd-missing-weight"]["error"],
        )
        self.assertIn(
            "required web field 'Combined' is missing",
            by_id["chevrolet-onix-2012-missing-combined"]["error"],
        )
        self.assertIn(
            "rule 'Unladen Weight' did not match acquired value",
            by_id["toyota-corolla-cross-2025-range-weight"]["error"],
        )
        self.assertIn(
            "rule 'Unladen Weight' did not match acquired value",
            by_id["nissan-pathfinder-2025-range-weight-epa-label"]["error"],
        )

    def test_partial_evidence_report_preserves_correct_fields_without_false_passes(self) -> None:
        dataset = load_web_extraction_corpus(DATASET)
        report = evaluate_web_extraction_partial_evidence_corpus(dataset)
        metrics = report["metrics"]
        by_id = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["artifact"], "AUTOEVOLUTION_ARTEGA_GT_RULES")
        self.assertEqual(report["datasetVersion"], "autoevolution-source-family-1.0")
        self.assertEqual(report["totalCases"], 12)
        self.assertEqual(metrics["casesWithoutIssues"], 8)
        self.assertEqual(metrics["casesWithIssues"], 4)
        self.assertEqual(metrics["issueCount"], 4)
        self.assertEqual(metrics["targetFieldCount"], 142)
        self.assertEqual(metrics["emittedFieldCount"], 140)
        self.assertEqual(metrics["correctFieldCount"], 140)
        self.assertEqual(metrics["incorrectFieldCount"], 0)
        self.assertEqual(metrics["unresolvedTargetFieldCount"], 2)
        self.assertEqual(metrics["fieldPrecision"], 1.0)
        self.assertEqual(metrics["fieldRecall"], 140 / 142)
        self.assertTrue(all(not case["incorrectFields"] for case in report["cases"]))

        self.assertEqual(
            by_id["bmw-g20-320i-rwd-missing-weight"]["issues"][0]["code"],
            "MISSING_FIELD",
        )
        self.assertEqual(
            by_id["chevrolet-onix-2012-missing-combined"]["issues"][0]["code"],
            "MISSING_FIELD",
        )
        self.assertEqual(
            by_id["toyota-corolla-cross-2025-range-weight"]["issues"][0]["code"],
            "PARSER_MISMATCH",
        )
        self.assertEqual(
            by_id["nissan-pathfinder-2025-range-weight-epa-label"]["issues"][0]["code"],
            "PARSER_MISMATCH",
        )
        self.assertEqual(
            by_id["nissan-pathfinder-2025-range-weight-epa-label"]["emittedFieldCount"],
            11,
        )

    def test_bounded_gold_is_additive_and_covers_only_non_scalar_targets(self) -> None:
        dataset = load_web_extraction_corpus(DATASET)
        bounded = load_web_extraction_bounded_gold(BOUNDED_GOLD, dataset)

        self.assertEqual(bounded.version, "autoevolution-bounded-curb-weight-1.0")
        self.assertEqual(bounded.base_dataset_version, dataset.version)
        self.assertEqual(bounded.artifact, "AUTOEVOLUTION_ARTEGA_GT_RULES_V2")
        self.assertEqual(
            bounded.expected_by_case,
            {
                "toyota-corolla-cross-2025-range-weight": {
                    "curb_weight": {"minValue": 1490, "maxValue": 1508}
                },
                "nissan-pathfinder-2025-range-weight-epa-label": {
                    "curb_weight": {"minValue": 1966, "maxValue": 2036}
                },
            },
        )

    def test_v2_bounded_artifact_resolves_range_targets_without_rewriting_v1(self) -> None:
        dataset = load_web_extraction_corpus(DATASET)
        bounded = load_web_extraction_bounded_gold(BOUNDED_GOLD, dataset)
        report = evaluate_web_extraction_bounded_corpus(dataset, bounded)
        metrics = report["metrics"]
        by_id = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["artifact"], "AUTOEVOLUTION_ARTEGA_GT_RULES_V2")
        self.assertEqual(
            report["datasetVersion"],
            "autoevolution-source-family-1.0+autoevolution-bounded-curb-weight-1.0",
        )
        self.assertEqual(metrics["pageSuccessCount"], 10)
        self.assertEqual(metrics["pageSuccessRate"], 10 / 12)
        self.assertEqual(metrics["explicitFailureCount"], 2)
        self.assertEqual(metrics["expectedOutcomeMatches"], 12)
        self.assertEqual(metrics["fullyCorrectPageCount"], 10)
        self.assertEqual(metrics["targetFieldCount"], 142)
        self.assertEqual(metrics["emittedFieldCount"], 120)
        self.assertEqual(metrics["correctFieldCount"], 120)
        self.assertEqual(metrics["fieldPrecision"], 1.0)
        self.assertEqual(metrics["fieldRecall"], 120 / 142)
        self.assertTrue(all(not case["incorrectFields"] for case in report["cases"]))

        self.assertEqual(
            by_id["toyota-corolla-cross-2025-range-weight"]["actualOutcome"],
            "SUCCESS",
        )
        self.assertEqual(
            by_id["nissan-pathfinder-2025-range-weight-epa-label"]["actualOutcome"],
            "SUCCESS",
        )
        self.assertEqual(
            by_id["bmw-g20-320i-rwd-missing-weight"]["actualOutcome"],
            "FAIL",
        )
        self.assertEqual(
            by_id["chevrolet-onix-2012-missing-combined"]["actualOutcome"],
            "FAIL",
        )

        historical = evaluate_web_extraction_corpus(dataset)
        self.assertEqual(historical["metrics"]["pageSuccessCount"], 8)
        self.assertEqual(historical["metrics"]["correctFieldCount"], 96)

    def test_v2_partial_evidence_resolves_all_source_targets_but_preserves_missing_issues(self) -> None:
        dataset = load_web_extraction_corpus(DATASET)
        bounded = load_web_extraction_bounded_gold(BOUNDED_GOLD, dataset)
        report = evaluate_web_extraction_bounded_partial_evidence_corpus(dataset, bounded)
        metrics = report["metrics"]
        by_id = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["totalCases"], 12)
        self.assertEqual(metrics["casesWithoutIssues"], 10)
        self.assertEqual(metrics["casesWithIssues"], 2)
        self.assertEqual(metrics["issueCount"], 2)
        self.assertEqual(metrics["targetFieldCount"], 142)
        self.assertEqual(metrics["emittedFieldCount"], 142)
        self.assertEqual(metrics["correctFieldCount"], 142)
        self.assertEqual(metrics["incorrectFieldCount"], 0)
        self.assertEqual(metrics["unresolvedTargetFieldCount"], 0)
        self.assertEqual(metrics["fieldPrecision"], 1.0)
        self.assertEqual(metrics["fieldRecall"], 1.0)
        self.assertTrue(all(not case["incorrectFields"] for case in report["cases"]))

        self.assertEqual(
            by_id["bmw-g20-320i-rwd-missing-weight"]["issues"][0]["code"],
            "MISSING_FIELD",
        )
        self.assertEqual(
            by_id["chevrolet-onix-2012-missing-combined"]["issues"][0]["code"],
            "MISSING_FIELD",
        )
        self.assertEqual(
            by_id["toyota-corolla-cross-2025-range-weight"]["issues"],
            [],
        )
        self.assertEqual(
            by_id["nissan-pathfinder-2025-range-weight-epa-label"]["issues"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
