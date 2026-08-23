import math
import unittest

from podium7.normalization import normalize_bounded_fact, normalize_fact


class NormalizationTests(unittest.TestCase):
    def test_power_hp_to_kw(self) -> None:
        result = normalize_fact("power", 300, "hp")
        self.assertEqual(result.unit, "kW")
        self.assertAlmostEqual(result.value, 223.709961, places=6)
        self.assertEqual(result.rule, "power.hp_to_kw.v1")

    def test_torque_nm_identity(self) -> None:
        result = normalize_fact("torque", 350, "Nm")
        self.assertEqual(result.value, 350)
        self.assertEqual(result.unit, "Nm")
        self.assertEqual(result.rule, "torque.nm.identity.v1")

    def test_displacement_l_to_cc(self) -> None:
        result = normalize_fact("displacement", 3.6, "L")
        self.assertEqual(result.value, 3600.0)
        self.assertEqual(result.unit, "cc")

    def test_dimension_inches_to_mm(self) -> None:
        result = normalize_fact("length", 158.1, "in")
        self.assertAlmostEqual(result.value, 4015.74, places=6)
        self.assertEqual(result.unit, "mm")

    def test_weight_lb_to_kg(self) -> None:
        result = normalize_fact("curb_weight", 2833, "lb")
        self.assertAlmostEqual(result.value, 1285.027184, places=6)
        self.assertEqual(result.unit, "kg")

    def test_bounded_weight_kg_preserves_explicit_bounds(self) -> None:
        result = normalize_bounded_fact("curb_weight", 1490, 1508, "kg")
        self.assertEqual(result.value, {"minValue": 1490, "maxValue": 1508})
        self.assertEqual(result.unit, "kg")
        self.assertEqual(result.rule, "curb_weight.bounded_to_kg.v1")

    def test_bounded_weight_lb_normalizes_each_bound(self) -> None:
        result = normalize_bounded_fact("curb_weight", 3285, 3325, "lb")
        self.assertEqual(
            result.value,
            {"minValue": 1490.050935, "maxValue": 1508.19463},
        )
        self.assertEqual(result.unit, "kg")

    def test_bounded_weight_rejects_reversed_bounds(self) -> None:
        with self.assertRaisesRegex(ValueError, "minimum cannot exceed maximum"):
            normalize_bounded_fact("curb_weight", 1508, 1490, "kg")

    def test_bounded_weight_rejects_non_finite_bounds(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_bounded_fact("curb_weight", value, 1508, "kg")
                with self.assertRaises(ValueError):
                    normalize_bounded_fact("curb_weight", 1490, value, "kg")

    def test_bounded_normalization_is_deliberately_narrow(self) -> None:
        with self.assertRaisesRegex(ValueError, "bounded normalization is unsupported"):
            normalize_bounded_fact("power", 100, 120, "kW")

    def test_consumption_mpg_us_to_l100km(self) -> None:
        result = normalize_fact("fuel_economy_combined", 24.5, "mpg-US")
        self.assertAlmostEqual(result.value, 9.600595, places=6)
        self.assertEqual(result.unit, "L/100km")

    def test_fuel_alias(self) -> None:
        result = normalize_fact("fuel_type", "Petrol", None)
        self.assertEqual(result.value, "gasoline")

    def test_transmission_token(self) -> None:
        result = normalize_fact("transmission", "  6-Speed   Automatic DSG ", None)
        self.assertEqual(result.value, "6-speed automatic dsg")

    def test_drivetrain_alias(self) -> None:
        result = normalize_fact("drivetrain", "Rear Wheel Drive", None)
        self.assertEqual(result.value, "rwd")

    def test_invalid_zero_mpg_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize_fact("fuel_economy_combined", 0, "mpg-US")

    def test_non_finite_converted_numeric_values_are_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_fact("power", value, "hp")

    def test_non_finite_identity_numeric_values_are_rejected(self) -> None:
        cases = (
            ("power", "kW"),
            ("torque", "Nm"),
            ("displacement", "cc"),
            ("length", "mm"),
            ("curb_weight", "kg"),
            ("fuel_economy_combined", "L/100km"),
        )
        for attribute, unit in cases:
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(attribute=attribute, unit=unit, value=value):
                    with self.assertRaises(ValueError):
                        normalize_fact(attribute, value, unit)


if __name__ == "__main__":
    unittest.main()
