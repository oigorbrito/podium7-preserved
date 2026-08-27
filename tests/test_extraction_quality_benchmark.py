import math
import unittest

from podium7.extraction_quality_benchmark import (
    ExtractionBenchmarkCase,
    evaluate_extraction_cases,
)


class ExtractionQualityBenchmarkTests(unittest.TestCase):
    def test_reports_extractbench_style_quality_dimensions(self):
        report = evaluate_extraction_cases(
            [
                ExtractionBenchmarkCase(
                    case_id="ev-spec-clean",
                    expected_fields={
                        "make": "Example",
                        "model": "E1",
                        "battery_kwh": 80,
                        "charging_ports": ["CCS", "Type 2"],
                    },
                    observed_fields={
                        "make": "Example",
                        "model": "E1",
                        "battery_kwh": 75,
                        "charging_ports": ["Type 2", "CCS"],
                        "invented_trim": "Ultra",
                    },
                    required_fields=frozenset({"make", "model", "battery_kwh"}),
                    evidence_by_field={
                        "make": ["ev:make"],
                        "model": ["ev:model"],
                        "battery_kwh": ["ev:battery"],
                        "charging_ports": ["ev:ports"],
                    },
                    schema_valid=True,
                    canonical_written_fields=frozenset({"make", "model", "battery_kwh"}),
                )
            ]
        )
        metrics = report["metrics"]
        self.assertEqual(1.0, metrics["schemaValidRate"])
        self.assertEqual(0.5, metrics["fieldCorrectness"])
        self.assertEqual(1.0, metrics["requiredFieldRecall"])
        self.assertEqual(0.2, metrics["hallucinatedFieldRate"])
        self.assertEqual(0.0, metrics["omittedFieldRate"])
        self.assertEqual(0.0, metrics["arrayAlignmentAccuracy"])
        self.assertEqual(0.8, metrics["evidenceLinkedFieldRate"])
        self.assertEqual(1, metrics["unsupportedCanonicalWriteCount"])
        self.assertAlmostEqual(1 / 3, metrics["unsupportedCanonicalWriteRate"])

    def test_safe_case_keeps_unsupported_canonical_write_rate_zero(self):
        report = evaluate_extraction_cases(
            [
                ExtractionBenchmarkCase(
                    case_id="safe",
                    expected_fields={"make": "Ford", "model": "Mustang"},
                    observed_fields={"make": "Ford", "model": "Mustang"},
                    required_fields=frozenset({"make", "model"}),
                    evidence_by_field={"make": ["e1"], "model": ["e2"]},
                    schema_valid=True,
                    canonical_written_fields=frozenset({"make", "model"}),
                )
            ]
        )
        self.assertEqual(0, report["metrics"]["unsupportedCanonicalWriteCount"])
        self.assertEqual(0.0, report["metrics"]["unsupportedCanonicalWriteRate"])

    def test_missing_evidence_makes_canonical_write_unsupported(self):
        report = evaluate_extraction_cases(
            [
                ExtractionBenchmarkCase(
                    case_id="missing-evidence",
                    expected_fields={"make": "Ford"},
                    observed_fields={"make": "Ford"},
                    required_fields=frozenset({"make"}),
                    evidence_by_field={},
                    schema_valid=True,
                    canonical_written_fields=frozenset({"make"}),
                )
            ]
        )
        self.assertEqual(["make"], report["observations"][0]["unsupportedCanonicalWrites"])

    def test_duplicate_case_ids_fail_closed(self):
        case = ExtractionBenchmarkCase(
            case_id="duplicate",
            expected_fields={"make": "Ford"},
            observed_fields={"make": "Ford"},
            required_fields=frozenset({"make"}),
            evidence_by_field={"make": ["e1"]},
            schema_valid=True,
        )
        with self.assertRaisesRegex(ValueError, "case_id values must be unique"):
            evaluate_extraction_cases([case, case])

    def test_invalid_field_evidence_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "evidence may only reference observed fields"):
            ExtractionBenchmarkCase(
                case_id="bad-evidence",
                expected_fields={"make": "Ford"},
                observed_fields={},
                required_fields=frozenset(),
                evidence_by_field={"make": ["e1"]},
                schema_valid=False,
            )
        with self.assertRaisesRegex(ValueError, "field evidence ids must be unique"):
            ExtractionBenchmarkCase(
                case_id="duplicate-evidence",
                expected_fields={"make": "Ford"},
                observed_fields={"make": "Ford"},
                required_fields=frozenset({"make"}),
                evidence_by_field={"make": ["e1", "e1"]},
                schema_valid=True,
            )

    def test_fixture_container_types_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "required_fields must be a frozenset"):
            ExtractionBenchmarkCase(
                case_id="wrong-required-type",
                expected_fields={"make": "Ford"},
                observed_fields={"make": "Ford"},
                required_fields={"make"},  # type: ignore[arg-type]
                evidence_by_field={"make": ["e1"]},
                schema_valid=True,
            )
        with self.assertRaisesRegex(ValueError, "canonical_written_fields must be a frozenset"):
            ExtractionBenchmarkCase(
                case_id="wrong-written-type",
                expected_fields={"make": "Ford"},
                observed_fields={"make": "Ford"},
                required_fields=frozenset({"make"}),
                evidence_by_field={"make": ["e1"]},
                schema_valid=True,
                canonical_written_fields={"make"},  # type: ignore[arg-type]
            )
        with self.assertRaisesRegex(ValueError, "observed_fields must be an object"):
            ExtractionBenchmarkCase(
                case_id="wrong-observed-type",
                expected_fields={"make": "Ford"},
                observed_fields=[],  # type: ignore[arg-type]
                required_fields=frozenset({"make"}),
                evidence_by_field={},
                schema_valid=False,
            )

    def test_non_json_and_non_finite_fixture_values_fail_closed(self):
        for value in (math.nan, math.inf, object()):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "strict JSON-compatible"):
                    ExtractionBenchmarkCase(
                        case_id=f"bad-value-{type(value).__name__}",
                        expected_fields={"value": value},
                        observed_fields={},
                        required_fields=frozenset(),
                        evidence_by_field={},
                        schema_valid=False,
                    )


if __name__ == "__main__":
    unittest.main()
