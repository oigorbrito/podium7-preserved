from pathlib import Path
import unittest

from podium7.fueleconomy_web_benchmark import (
    evaluate_fueleconomy_corpus,
    load_fueleconomy_corpus,
)
from podium7.web_extraction import (
    FUELECONOMY_GOV_VEHICLE_RULES_V1,
    extract_fueleconomy_gov_vehicle,
    extract_with_rules,
    extract_with_rules_report,
)


ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "benchmarks" / "web_extraction_fueleconomy_source_family_v1.json"
SNAPSHOT_DIR = ROOT / "data" / "raw" / "web" / "fueleconomy-v1"


class FuelEconomyWebExtractionTests(unittest.TestCase):
    def test_corpus_is_frozen_source_backed_and_classifies_every_target(self):
        corpus = load_fueleconomy_corpus(CORPUS_PATH)
        self.assertEqual(corpus.version, "fueleconomy-find-a-car-source-family-1.0")
        self.assertEqual(len(corpus.cases), 4)
        self.assertEqual({case.expected_outcome for case in corpus.cases}, {"SUCCESS", "FAIL"})
        for case in corpus.cases:
            self.assertTrue(case.snapshot_path.is_file())
            self.assertEqual(case.source_target_field_count, 3)
            self.assertEqual(
                len(case.expected_parsed) + len(case.unsupported_target_fields),
                case.source_target_field_count,
            )

    def test_f150_strict_extraction_uses_source_specific_provenance(self):
        text = (SNAPSHOT_DIR / "ford-f150-hev-2025.txt").read_text(encoding="utf-8")
        facts = {fact.attribute: fact for fact in extract_fueleconomy_gov_vehicle(text)}

        self.assertEqual(set(facts), {"fuel_economy_combined", "drivetrain", "fuel_type"})
        self.assertEqual(facts["fuel_economy_combined"].parsed_value, 23)
        self.assertAlmostEqual(
            facts["fuel_economy_combined"].normalized_value,
            235.214583 / 23,
            places=6,
        )
        self.assertEqual(facts["fuel_economy_combined"].unit, "L/100km")
        self.assertEqual(facts["fuel_economy_combined"].extraction_rule, "fueleconomy_gov.fuel_economy_combined.v1")
        self.assertEqual(facts["drivetrain"].normalized_value, "4wd")
        self.assertTrue(all(fact.extraction_rule.startswith("fueleconomy_gov.") for fact in facts.values()))

    def test_phev_gas_only_label_is_explicit_alias_with_provenance(self):
        text = (SNAPSHOT_DIR / "toyota-rav4-prime-2021.txt").read_text(encoding="utf-8")
        facts = {fact.attribute: fact for fact in extract_fueleconomy_gov_vehicle(text)}
        economy = facts["fuel_economy_combined"]

        self.assertEqual(economy.parsed_value, 38)
        self.assertEqual(economy.source_label, "Combined MPG on Gas Only")
        self.assertEqual(facts["drivetrain"].normalized_value, "awd")

    def test_mpge_is_not_silently_converted_as_gasoline_mpg(self):
        text = (SNAPSHOT_DIR / "tesla-model-3-long-range-awd-2022.txt").read_text(encoding="utf-8")
        report = extract_with_rules_report(
            text,
            FUELECONOMY_GOV_VEHICLE_RULES_V1,
            rule_namespace="fueleconomy_gov",
        )

        self.assertEqual(len(report.facts), 2)
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0].code, "PARSER_MISMATCH")
        self.assertEqual(report.issues[0].attribute, "fuel_economy_combined")
        self.assertEqual(report.issues[0].raw_value, "131 MPGe")
        with self.assertRaisesRegex(ValueError, "131 MPGe"):
            extract_fueleconomy_gov_vehicle(text)

    def test_strict_corpus_metrics_match_independent_gold(self):
        report = evaluate_fueleconomy_corpus(load_fueleconomy_corpus(CORPUS_PATH))
        metrics = report["metrics"]

        self.assertEqual(metrics["pageSuccessCount"], 2)
        self.assertEqual(metrics["explicitFailureCount"], 2)
        self.assertEqual(metrics["expectedOutcomeMatches"], 4)
        self.assertEqual(metrics["targetFieldCount"], 12)
        self.assertEqual(metrics["emittedFieldCount"], 6)
        self.assertEqual(metrics["correctFieldCount"], 6)
        self.assertEqual(metrics["fieldPrecision"], 1.0)
        self.assertEqual(metrics["fieldRecall"], 0.5)

    def test_partial_corpus_preserves_valid_facts_and_explicit_semantic_gap(self):
        report = evaluate_fueleconomy_corpus(
            load_fueleconomy_corpus(CORPUS_PATH),
            partial_evidence=True,
        )
        metrics = report["metrics"]

        self.assertEqual(metrics["casesWithoutIssues"], 2)
        self.assertEqual(metrics["casesWithIssues"], 2)
        self.assertEqual(metrics["issueCount"], 2)
        self.assertEqual(metrics["targetFieldCount"], 12)
        self.assertEqual(metrics["emittedFieldCount"], 10)
        self.assertEqual(metrics["correctFieldCount"], 10)
        self.assertEqual(metrics["incorrectFieldCount"], 0)
        self.assertEqual(metrics["unresolvedTargetFieldCount"], 2)
        self.assertEqual(metrics["fieldPrecision"], 1.0)
        self.assertAlmostEqual(metrics["retainedFieldRecall"], 10 / 12)
        issue_attributes = [
            attribute
            for case in report["cases"]
            for attribute in case["issueAttributes"]
        ]
        self.assertEqual(issue_attributes, ["fuel_economy_combined", "fuel_economy_combined"])

    def test_bolt_partial_facts_keep_drive_and_fuel(self):
        text = (SNAPSHOT_DIR / "chevrolet-bolt-ev-2017.txt").read_text(encoding="utf-8")
        report = extract_with_rules_report(
            text,
            FUELECONOMY_GOV_VEHICLE_RULES_V1,
            rule_namespace="fueleconomy_gov",
        )
        facts = {fact.attribute: fact for fact in report.facts}

        self.assertEqual(facts["drivetrain"].normalized_value, "fwd")
        self.assertEqual(facts["fuel_type"].normalized_value, "electric")
        self.assertEqual(report.issues[0].raw_value, "119 MPGe")

    def test_rule_namespace_is_validated_and_default_remains_compatible(self):
        text = "Drive: | All-Wheel Drive\n"
        drive_rule = (FUELECONOMY_GOV_VEHICLE_RULES_V1[1],)
        default_fact = extract_with_rules(text, drive_rule)[0]
        self.assertEqual(default_fact.extraction_rule, "autoevolution.drivetrain.v1")
        with self.assertRaisesRegex(ValueError, "rule_namespace"):
            extract_with_rules(text, drive_rule, rule_namespace="Fuel Economy")


if __name__ == "__main__":
    unittest.main()
