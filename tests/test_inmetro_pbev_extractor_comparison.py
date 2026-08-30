import hashlib
import json
import unittest
from pathlib import Path

from podium7.extraction_quality_benchmark import ExtractionBenchmarkCase, evaluate_extraction_cases


class InmetroPbevExtractorComparisonTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(
            Path("benchmarks/inmetro_pbev_extractor_comparison_v1.json").read_text(encoding="utf-8")
        )

    def test_comparison_is_bound_to_exact_retained_pdf(self):
        fixture = Path(self.payload["source"]["fixture"])
        self.assertTrue(fixture.is_file())
        self.assertEqual(
            self.payload["source"]["sha256"],
            hashlib.sha256(fixture.read_bytes()).hexdigest(),
        )
        self.assertEqual(1, self.payload["source"]["page"])

    def test_retained_observations_reproduce_quality_metrics(self):
        required = frozenset(self.payload["authorizedFields"])
        expected_metrics = {
            "schemaValidRate": 1.0,
            "fieldCorrectness": 1.0,
            "requiredFieldRecall": 1.0,
            "hallucinatedFieldRate": 0.0,
            "omittedFieldRate": 0.0,
            "evidenceLinkedFieldRate": 1.0,
            "unsupportedCanonicalWriteRate": 0.0,
        }
        for observed_key, metrics_key in (
            ("baselineObserved", "baselineMetrics"),
            ("candidateObserved", "candidateMetrics"),
        ):
            cases = []
            for item in self.payload["cases"]:
                evidence = {
                    field: (f"{self.payload['source']['sha256']}#page=1;case={item['id']};field={field}",)
                    for field in item[observed_key]
                }
                cases.append(
                    ExtractionBenchmarkCase(
                        case_id=item["id"],
                        expected_fields=item["expected"],
                        observed_fields=item[observed_key],
                        required_fields=required,
                        evidence_by_field=evidence,
                        schema_valid=True,
                        canonical_written_fields=frozenset(),
                    )
                )
            report = evaluate_extraction_cases(cases)
            for metric, expected in expected_metrics.items():
                self.assertEqual(expected, report["metrics"][metric])
                self.assertEqual(expected, self.payload[metrics_key][metric])

    def test_disposition_does_not_adopt_candidate_without_material_gain(self):
        self.assertEqual("NO_MATERIAL_GAIN", self.payload["disposition"])
        self.assertEqual(18, self.payload["preRemediationFinding"]["baselineCorrectFields"])
        self.assertEqual(21, self.payload["preRemediationFinding"]["expectedFields"])
        self.assertEqual([257, 259], self.payload["preRemediationFinding"]["remediationIssues"])
        self.assertTrue(self.payload["scopeLimits"]["quantitativeColumnsExcluded"])
        self.assertEqual("0.11.9", self.payload["environment"]["pdfplumber"])
        self.assertEqual("1.0.9", self.payload["environment"]["camelot-py"])


if __name__ == "__main__":
    unittest.main()
