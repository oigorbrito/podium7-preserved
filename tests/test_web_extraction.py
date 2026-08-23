import unittest

from podium7.web_extraction import (
    AUTOEVOLUTION_ARTEGA_GT_RULES,
    extract_autoevolution_artega_gt,
    extract_with_rules,
    extract_with_rules_report,
)


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
        self.assertEqual(facts["power"].source_label, "Power")

    def test_repeated_runs_are_identical(self):
        first = extract_autoevolution_artega_gt(SNAPSHOT)
        second = extract_autoevolution_artega_gt(SNAPSHOT)
        self.assertEqual(first, second)

    def test_changed_structure_fails_explicitly(self):
        broken = SNAPSHOT.replace("Power: |", "Power =>")
        with self.assertRaises(ValueError):
            extract_autoevolution_artega_gt(broken)

    def test_duplicate_label_fails_explicitly(self):
        duplicated = SNAPSHOT + "POWER: | 220.6 KW @ 6600 RPM / 300 HP @ 6600 RPM\n"
        with self.assertRaises(ValueError):
            extract_autoevolution_artega_gt(duplicated)

    def test_report_preserves_valid_facts_when_required_field_is_missing(self):
        partial = SNAPSHOT.replace("Unladen Weight: | 2833 lbs (1285 kg)\n", "")
        report = extract_with_rules_report(partial, AUTOEVOLUTION_ARTEGA_GT_RULES)

        self.assertEqual(len(report.facts), 11)
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0].attribute, "curb_weight")
        self.assertEqual(report.issues[0].code, "MISSING_FIELD")
        self.assertIn("required web field 'Unladen Weight' is missing", report.issues[0].message)

        with self.assertRaisesRegex(ValueError, "required web field 'Unladen Weight' is missing"):
            extract_with_rules(partial, AUTOEVOLUTION_ARTEGA_GT_RULES)

    def test_report_preserves_other_facts_without_collapsing_weight_range(self):
        ranged = SNAPSHOT.replace(
            "Unladen Weight: | 2833 lbs (1285 kg)",
            "Unladen Weight: | 3300-3500 lbs (1497-1588 kg)",
        )
        report = extract_with_rules_report(ranged, AUTOEVOLUTION_ARTEGA_GT_RULES)
        by_attribute = {fact.attribute: fact for fact in report.facts}

        self.assertEqual(len(report.facts), 11)
        self.assertNotIn("curb_weight", by_attribute)
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0].attribute, "curb_weight")
        self.assertEqual(report.issues[0].label, "Unladen Weight")
        self.assertEqual(report.issues[0].code, "PARSER_MISMATCH")
        self.assertEqual(report.issues[0].raw_value, "3300-3500 lbs (1497-1588 kg)")

    def test_declared_label_alias_is_supported(self):
        variant = SNAPSHOT.replace("Combined: |", "Combined (EPA): |")
        facts = {fact.attribute: fact for fact in extract_autoevolution_artega_gt(variant)}
        self.assertEqual(facts["fuel_economy_combined"].parsed_value, 9.6)
        self.assertEqual(facts["fuel_economy_combined"].source_label, "Combined (EPA)")

    def test_canonical_and_alias_labels_together_are_ambiguous(self):
        ambiguous = SNAPSHOT + "Combined (EPA): | 24.5 mpg US (9.6 L/100Km)\n"
        report = extract_with_rules_report(ambiguous, AUTOEVOLUTION_ARTEGA_GT_RULES)

        self.assertEqual(len(report.facts), 11)
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0].attribute, "fuel_economy_combined")
        self.assertEqual(report.issues[0].code, "AMBIGUOUS_LABEL")
        with self.assertRaisesRegex(ValueError, "multiple web labels matched rule 'Combined'"):
            extract_with_rules(ambiguous, AUTOEVOLUTION_ARTEGA_GT_RULES)


if __name__ == "__main__":
    unittest.main()
