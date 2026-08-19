import unittest

from podium7.normalization import normalize_fact


class TextNormalizationValueTests(unittest.TestCase):
    def test_known_text_attributes_reject_empty_values(self):
        for attribute in ("fuel_type", "transmission", "drivetrain"):
            for value in ("", "   ", "\t\n"):
                with self.subTest(attribute=attribute, value=value):
                    with self.assertRaises(ValueError):
                        normalize_fact(attribute, value, None)

    def test_known_text_attributes_reject_non_text_values(self):
        for attribute in ("fuel_type", "transmission", "drivetrain"):
            for value in (123, True, {"value": "text"}):
                with self.subTest(attribute=attribute, value=value):
                    with self.assertRaises(ValueError):
                        normalize_fact(attribute, value, None)


if __name__ == "__main__":
    unittest.main()
