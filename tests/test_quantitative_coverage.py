from pathlib import Path
import json
import tempfile
import unittest

from podium7.enrichment_contract import CONTRACT_FIELDS
from podium7.quantitative_coverage import (
    COVERAGE_SCHEMA,
    RESULT_SCHEMA,
    load_coverage_fixture,
    records_comparable,
    render_coverage_result,
    run_coverage_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "benchmarks/brazil_quantitative_coverage_v1.json"


class QuantitativeCoverageTests(unittest.TestCase):
    def test_fixture_is_deterministic_and_complete(self) -> None:
        fixture = load_coverage_fixture(FIXTURE)
        self.assertEqual(fixture["schema"], COVERAGE_SCHEMA)
        self.assertEqual(fixture["source"]["market"], "BR")
        vehicle_ids = {row["vehicleId"] for row in fixture["records"]}
        self.assertEqual(len(vehicle_ids), 3)
        self.assertEqual(len(fixture["records"]), len(vehicle_ids) * len(CONTRACT_FIELDS))
        self.assertEqual(fixture["records"], sorted(fixture["records"], key=lambda row: (row["field"], row["vehicleId"])))

    def test_retained_brazil_baseline_does_not_invent_quantitative_values(self) -> None:
        result = run_coverage_benchmark(FIXTURE)
        self.assertEqual(result["schema"], RESULT_SCHEMA)
        self.assertEqual(len(result["contentSha256"]), 64)
        for row in result["records"]:
            self.assertEqual(row["knowledgeState"], "unknown")
            self.assertFalse(row["publicationEligible"])
            self.assertIsNone(row["value"])
            self.assertIsNone(row["unit"])
            self.assertIn("identity/table fields only", row["reason"])
        for field in result["fields"]:
            self.assertEqual(field["denominator"], 3)
            self.assertEqual(field["knownPublicationReady"], 0)
            self.assertEqual(field["unknownOrNotPublishable"], 3)
            self.assertEqual(field["unresolvedConflict"], 0)
            self.assertEqual(field["vehiclesComparableWithDistinctPeer"], 0)

    def test_structural_control_is_separate_from_brazil_denominator(self) -> None:
        result = run_coverage_benchmark(FIXTURE)
        control = result["structuralControl"]
        self.assertEqual(control["sourceFamily"], "AUTOEVOLUTION_RETAINED_WEB_CORPUS")
        self.assertEqual(control["knownExample"]["field"], "curb_weight")
        self.assertEqual(control["knownExample"]["unit"], "kg")
        self.assertNotEqual(control["sourceFamily"], result["source"]["family"])
        self.assertEqual(sum(field["denominator"] for field in result["fields"]), 27)

    def test_identical_semantic_context_allows_distinct_vehicle_pair(self) -> None:
        left = {
            "vehicleId": "podium7:vehicle:a",
            "field": "curb_weight",
            "knowledgeState": "known",
            "publicationEligible": True,
            "unit": "kg",
            "context": {"market": "BR", "methodology": "curb mass"},
        }
        right = {**left, "vehicleId": "podium7:vehicle:b"}
        self.assertTrue(records_comparable(left, right))

    def test_context_mismatch_blocks_comparable_pair(self) -> None:
        left = {
            "vehicleId": "podium7:vehicle:a",
            "field": "fuel_economy_combined",
            "knowledgeState": "known",
            "publicationEligible": True,
            "unit": "km/l",
            "context": {"market": "BR", "methodology": "cycle-a"},
        }
        right = {**left, "vehicleId": "podium7:vehicle:b", "context": {"market": "BR", "methodology": "cycle-b"}}
        self.assertFalse(records_comparable(left, right))

    def test_unresolved_conflict_remains_non_publishable(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        target = next(row for row in payload["records"] if row["field"] == "power")
        target["conflict"] = {
            "provenanceRefs": ["source:a", "source:b"],
            "reason": "retained sources disagree",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_coverage_benchmark(path)
        power = next(field for field in result["fields"] if field["field"] == "power")
        self.assertEqual(power["unresolvedConflict"], 1)
        self.assertEqual(power["knownPublicationReady"], 0)

    def test_rerun_is_byte_stable(self) -> None:
        first = render_coverage_result(FIXTURE)
        second = render_coverage_result(FIXTURE)
        self.assertEqual(first, second)
        first_payload = json.loads(first)
        self.assertEqual(first_payload["contentSha256"], json.loads(second)["contentSha256"])

    def test_catalog_json_2_contract_is_not_mutated(self) -> None:
        catalog_contract = (ROOT / "docs/CATALOG-JSON-CONTRACT-V2.md").read_text(encoding="utf-8")
        self.assertNotIn("quantitative-coverage-benchmark", catalog_contract)
        self.assertNotIn("quantitative-enrichment.v1", catalog_contract)


if __name__ == "__main__":
    unittest.main()
