import unittest

from podium7.web_extraction import extract_autoevolution_artega_gt


SNAPSHOT = """Displacement: | 3597 cm3 (220 ci)
Power: | 220.6 KW @ 6600 RPM / 300 HP @ 6600 RPM / 296 BHP @ 6600 RPM
Torque: | 258 lb-ft @ 2500-5000 RPM / 350 Nm @ 2500-5000 RPM
Fuel: | Gasoline
Drive Type: | Rear Wheel Drive
Gearbox: | 6-speed automatic DSG
Length: | 158.1 in (4016 mm)
Width: | 74.1 in (1882 mm)
Height: | 46.5 in (1181 mm)
Wheelbase: | 103.9 in (2639 mm)
Unladen Weight: | 2833 lbs (1285 kg)
Combined: | 24.5 mpg US (9.6 L/100Km)
"""


class WebExtractionTests(unittest.TestCase):
    def test_compiled_rules_extract_expected_fields(self):
        facts = extract_autoevolution_artega_gt(SNAPSHOT)
        self.assertEqual(len(facts), 12)

    def test_power_is_normalized(self):
        facts = {fact.attribute: fact for fact in extract_autoevolution_artega_gt(SNAPSHOT)}
        self.assertEqual(facts["power"].parsed_value, 300)
        self.assertEqual(facts["power"].unit, "kW")
        self.assertEqual(facts["power"].normalized_value, 223.709961)

    def test_repeated_runs_are_identical(self):
        first = extract_autoevolution_artega_gt(SNAPSHOT)
        second = extract_autoevolution_artega_gt(SNAPSHOT)
        self.assertEqual(first, second)

    def test_changed_structure_fails_explicitly(self):
        broken = SNAPSHOT.replace("Power: |", "Power =>")
        facts = extract_autoevolution_artega_gt(broken)
        attributes = {fact.attribute for fact in facts}
        self.assertNotIn("power", attributes)


if __name__ == "__main__":
    unittest.main()
