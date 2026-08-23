from __future__ import annotations

from pathlib import Path
import unittest

from podium7.eea_benchmark import evaluate_eea_corpus, load_eea_corpus
from podium7.eea_source import (
    extract_eea_record,
    extract_eea_record_report,
    load_eea_response,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "eea_source_family_v1.json"


class EeaSourceFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_eea_corpus(CORPUS)
        cls.rows = {
            row["ID"]: row
            for row in load_eea_response(cls.corpus.snapshot_path.read_bytes())
        }

    def test_frozen_corpus_is_exact_four_row_pinned_slice(self) -> None:
        self.assertEqual(4, len(self.corpus.cases))
        self.assertEqual(1165, self.corpus.snapshot_size_bytes)
        self.assertEqual(
            "847fa97a46ae32d60673fe63b5ebeeb2d35575771c607b806e3bdedd1c7d2ec9",
            self.corpus.snapshot_sha256,
        )
        self.assertEqual(
            {162744190, 162744191, 162744196, 162744197},
            set(self.rows),
        )

    def test_strict_benchmark_is_four_of_four_with_zero_incorrect_fields(self) -> None:
        report = evaluate_eea_corpus(self.corpus)
        metrics = report["metrics"]
        self.assertEqual("strict", report["mode"])
        self.assertEqual(4, metrics["strictSuccessCount"])
        self.assertEqual(1.0, metrics["strictSuccessRate"])
        self.assertEqual(11, metrics["targetFieldCount"])
        self.assertEqual(11, metrics["emittedFieldCount"])
        self.assertEqual(11, metrics["correctFieldCount"])
        self.assertEqual(0, metrics["incorrectFieldCount"])
        self.assertEqual(1.0, metrics["fieldPrecision"])
        self.assertEqual(1.0, metrics["fieldRecall"])

    def test_partial_benchmark_retains_all_eleven_supported_targets(self) -> None:
        report = evaluate_eea_corpus(self.corpus, partial_evidence=True)
        metrics = report["metrics"]
        self.assertEqual("partial-evidence", report["mode"])
        self.assertEqual(4, metrics["casesWithoutIssues"])
        self.assertEqual(0, metrics["casesWithIssues"])
        self.assertEqual(0, metrics["issueCount"])
        self.assertEqual(11, metrics["correctFieldCount"])
        self.assertEqual(0, metrics["incorrectFieldCount"])
        self.assertEqual(0, metrics["unresolvedTargetFieldCount"])
        self.assertEqual(1.0, metrics["fieldPrecision"])
        self.assertEqual(1.0, metrics["retainedFieldRecall"])

    def test_mass_in_running_order_is_preserved_but_not_promoted_to_curb_weight(self) -> None:
        report = extract_eea_record(self.rows[162744191])
        self.assertEqual(1770, report.regulatory.mass_in_running_order_kg)
        self.assertNotIn("curb_weight", {fact.attribute for fact in report.facts})
        self.assertEqual(
            {"fuel_type": "hybrid", "power": 190, "displacement": 1999},
            {fact.attribute: fact.normalized_value for fact in report.facts},
        )

    def test_electric_record_does_not_invent_displacement(self) -> None:
        report = extract_eea_record(self.rows[162744190])
        self.assertEqual((), report.issues)
        self.assertIsNone(report.regulatory.engine_capacity_cm3)
        self.assertEqual(
            {"fuel_type": "electric", "power": 200},
            {fact.attribute: fact.normalized_value for fact in report.facts},
        )

    def test_plugin_hybrid_requires_declared_fuel_type_and_mode_pair(self) -> None:
        report = extract_eea_record(self.rows[162744196])
        facts = {fact.attribute: fact.normalized_value for fact in report.facts}
        self.assertEqual("plug_in_hybrid", facts["fuel_type"])
        self.assertEqual(1969, facts["displacement"])
        self.assertEqual(186, facts["power"])

    def test_unknown_fuel_mode_is_explicit_partial_issue(self) -> None:
        row = dict(self.rows[162744197])
        row["Fm"] = "X"
        report = extract_eea_record_report(row)
        self.assertIn("UNSUPPORTED_FUEL_SEMANTICS", [issue.code for issue in report.issues])
        self.assertNotIn("fuel_type", {fact.attribute for fact in report.facts})
        with self.assertRaisesRegex(ValueError, "unsupported EEA fuel type/mode"):
            extract_eea_record(row)

    def test_missing_required_power_is_explicit_without_dropping_other_partial_facts(self) -> None:
        row = dict(self.rows[162744197])
        row["Ep (KW)"] = None
        report = extract_eea_record_report(row)
        self.assertIn("MISSING_FACT", [issue.code for issue in report.issues])
        self.assertEqual(
            {"fuel_type": "gasoline", "displacement": 999},
            {fact.attribute: fact.normalized_value for fact in report.facts},
        )
        with self.assertRaisesRegex(ValueError, r"Ep \(KW\).+missing"):
            extract_eea_record(row)

    def test_duplicate_source_record_ids_are_rejected(self) -> None:
        payload = '{"results":[{"ID":1},{"ID":1}]}'
        with self.assertRaisesRegex(ValueError, "duplicate EEA source record ID 1"):
            load_eea_response(payload)

    def test_non_standard_json_constants_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-standard JSON constant"):
            load_eea_response('{"results":[{"ID":1,"Ep (KW)":NaN}]}')


if __name__ == "__main__":
    unittest.main()
