import unittest

from podium7.normalization import normalize_fact


class NormalizationUnitContractTests(unittest.TestCase):
    def test_known_numeric_attributes_reject_unsupported_units(self):
        cases = (
            ("power", 1000, "W"),
            ("torque", 100, "N"),
            ("displacement", 3.6, "m3"),
            ("length", 400, "cm"),
            ("curb_weight", 1200000, "g"),
            ("fuel_economy_combined", 30, "mpg-UK"),
            ("zero_to_hundred", 5, "ms"),
            ("top_speed", 200, "mph"),
        )
        for attribute, value, unit in cases:
            with self.subTest(attribute=attribute, unit=unit):
                with self.assertRaises(ValueError):
                    normalize_fact(attribute, value, unit)

    def test_unitless_known_attributes_reject_units(self):
        cases = (
            ("cylinders", 6, "count"),
            ("fuel_type", "Gasoline", "text"),
            ("transmission", "6-speed automatic", "text"),
            ("drivetrain", "Rear Wheel Drive", "text"),
        )
        for attribute, value, unit in cases:
            with self.subTest(attribute=attribute):
                with self.assertRaises(ValueError):
                    normalize_fact(attribute, value, unit)

    def test_structured_numeric_identity_units_have_explicit_rules(self):
        cylinders = normalize_fact("cylinders", 6, None)
        zero_to_hundred = normalize_fact("zero_to_hundred", 4.8, "s")
        top_speed = normalize_fact("top_speed", 270, "km/h")
        self.assertEqual((cylinders.value, cylinders.rule), (6, "cylinders.count.identity.v1"))
        self.assertEqual((zero_to_hundred.value, zero_to_hundred.rule), (4.8, "zero_to_hundred.seconds.identity.v1"))
        self.assertEqual((top_speed.value, top_speed.rule), (270, "top_speed.kmh.identity.v1"))

    def test_unknown_attribute_remains_explicit_unspecified_identity(self):
        result = normalize_fact("future_metric", "source-value", "source-unit")
        self.assertEqual(result.value, "source-value")
        self.assertEqual(result.unit, "source-unit")
        self.assertEqual(result.rule, "identity.unspecified.v1")


if __name__ == "__main__":
    unittest.main()
