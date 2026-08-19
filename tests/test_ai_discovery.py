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


if __name__ == "__main__":
    unittest.main()
