import unittest
from collections import Counter
from pathlib import Path

from podium7.web_extraction_benchmark import (
    evaluate_web_extraction_corpus,
    load_web_extraction_corpus,
)


DATASET = (
    Path(__file__).resolve().parents[1]
    / "benchmarks"
    / "web_extraction_source_family_corpus_v1.json"
)


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


if __name__ == "__main__":
    unittest.main()
