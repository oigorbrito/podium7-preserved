import unittest

from podium7.ai_discovery import validate_extraction_artifact
from podium7.web_extraction import extract_with_rules


VALID = {
    "source_id": "example-source",
    "rules": [
        {"label": "Power", "attribute": "power", "parser": r"(\d+) HP", "source_unit": "hp"}
    ],
}


class AIDiscoveryTests(unittest.TestCase):
    def test_valid_artifact_compiles(self):
        artifact = validate_extraction_artifact(VALID)
        self.assertEqual(artifact.source_id, "example-source")
        self.assertEqual(artifact.rules[0].attribute, "power")
        self.assertEqual(artifact.artifact_version, "v1")

    def test_missing_required_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_extraction_artifact({"source_id": "x", "rules": [{"label": "Power"}]})

    def test_invalid_regex_is_rejected(self):
        payload = {"source_id": "x", "rules": [{"label": "Power", "attribute": "power", "parser": "([", "source_unit": "hp"}]}
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_validated_artifact_is_reusable(self):
        artifact = validate_extraction_artifact(VALID)
        text = "Power: | 300 HP"
        first = extract_with_rules(text, artifact.rules)
        second = extract_with_rules(text, artifact.rules)
        self.assertEqual(first, second)
        self.assertEqual(first[0].normalized_value, 223.709961)

    def test_duplicate_attribute_after_normalization_is_rejected(self):
        payload = {
            "source_id": "x",
            "rules": [
                {"label": "Power", "attribute": "power", "parser": r"(\d+) HP", "source_unit": "hp"},
                {"label": "Power Alt", "attribute": " POWER ", "parser": r"(\d+) HP", "source_unit": "hp"},
            ],
        }
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_duplicate_label_after_normalization_is_rejected(self):
        payload = {
            "source_id": "x",
            "rules": [
                {"label": "Power", "attribute": "power", "parser": r"(\d+) HP", "source_unit": "hp"},
                {"label": " power ", "attribute": "torque", "parser": r"(\d+) Nm", "source_unit": "Nm"},
            ],
        }
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_blank_source_unit_is_rejected(self):
        payload = {
            "source_id": "x",
            "rules": [
                {"label": "Power", "attribute": "power", "parser": r"(\d+) HP", "source_unit": "   "}
            ],
        }
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_label_aliases_compile_and_are_reusable(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Combined",
                    "label_aliases": ["Combined (EPA)"],
                    "attribute": "fuel_economy_combined",
                    "parser": r"([\d.]+) L/100Km",
                    "source_unit": "L/100km",
                }
            ],
        }
        artifact = validate_extraction_artifact(payload)
        self.assertEqual(artifact.rules[0].label_aliases, ("Combined (EPA)",))
        facts = extract_with_rules("Combined (EPA): | 9.6 L/100Km", artifact.rules)
        self.assertEqual(facts[0].parsed_value, 9.6)

    def test_alias_cannot_duplicate_canonical_label(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Combined",
                    "label_aliases": [" combined "],
                    "attribute": "fuel_economy_combined",
                    "parser": r"([\d.]+) L/100Km",
                    "source_unit": "L/100km",
                }
            ],
        }
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_alias_cannot_collide_with_another_rule_label(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Combined",
                    "label_aliases": ["Combined (EPA)"],
                    "attribute": "fuel_economy_combined",
                    "parser": r"([\d.]+) L/100Km",
                    "source_unit": "L/100km",
                },
                {
                    "label": " combined (epa) ",
                    "attribute": "power",
                    "parser": r"(\d+) HP",
                    "source_unit": "hp",
                },
            ],
        }
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_label_aliases_must_be_non_empty_strings(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Power",
                    "label_aliases": [""],
                    "attribute": "power",
                    "parser": r"(\d+) HP",
                    "source_unit": "hp",
                }
            ],
        }
        with self.assertRaises(ValueError):
            validate_extraction_artifact(payload)

    def test_bounded_weight_parser_compiles_and_extracts_bounds(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Unladen Weight",
                    "attribute": "curb_weight",
                    "parser": r"\((\d+) kg\)",
                    "range_parser": r"\((\d+)\s*-\s*(\d+) kg\)",
                    "source_unit": "kg",
                }
            ],
        }
        artifact = validate_extraction_artifact(payload)
        self.assertEqual(artifact.artifact_version, "v2")
        self.assertEqual(artifact.rules[0].range_parser, r"\((\d+)\s*-\s*(\d+) kg\)")
        facts = extract_with_rules(
            "Unladen Weight: | 3285 - 3325 lbs (1490 - 1508 kg)",
            artifact.rules,
        )
        self.assertEqual(
            facts[0].normalized_value,
            {"minValue": 1490, "maxValue": 1508},
        )

    def test_bounded_parser_requires_exactly_two_capture_groups(self):
        for range_parser in (r"(\d+)", r"(\d+)-(\d+)-(\d+)"):
            with self.subTest(range_parser=range_parser):
                payload = {
                    "source_id": "x",
                    "rules": [
                        {
                            "label": "Unladen Weight",
                            "attribute": "curb_weight",
                            "parser": r"(\d+) kg",
                            "range_parser": range_parser,
                            "source_unit": "kg",
                        }
                    ],
                }
                with self.assertRaisesRegex(ValueError, "exactly two capture groups"):
                    validate_extraction_artifact(payload)

    def test_bounded_parser_is_rejected_for_unsupported_attribute(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Power",
                    "attribute": "power",
                    "parser": r"(\d+) kW",
                    "range_parser": r"(\d+)\s*-\s*(\d+) kW",
                    "source_unit": "kW",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "bounded range parsing is unsupported"):
            validate_extraction_artifact(payload)

    def test_bounded_weight_parser_rejects_unsupported_source_unit(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Unladen Weight",
                    "attribute": "curb_weight",
                    "parser": r"(\d+) stone",
                    "range_parser": r"(\d+)\s*-\s*(\d+) stone",
                    "source_unit": "stone",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "requires kg, lb, or lbs"):
            validate_extraction_artifact(payload)

    def test_invalid_bounded_parser_regex_is_rejected(self):
        payload = {
            "source_id": "x",
            "rules": [
                {
                    "label": "Unladen Weight",
                    "attribute": "curb_weight",
                    "parser": r"(\d+) kg",
                    "range_parser": "([",
                    "source_unit": "kg",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "range_parser is invalid"):
            validate_extraction_artifact(payload)


if __name__ == "__main__":
    unittest.main()
