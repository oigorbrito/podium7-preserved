import json
import unittest
from pathlib import Path

from podium7.br_pbev_technical_sheet import (
    CONTRACT_FIELDS,
    CONTRACT_SCHEMA,
    PbevTechnicalSheetFact,
    publish_pbev_technical_sheet_payload,
    publish_pbev_technical_sheets_from_benchmark,
)
from podium7.inmetro_pbev_benchmark import load_inmetro_pbev_quantitative_benchmark


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "benchmarks" / "inmetro_pbev_quantitative_semantics_v1.json"


class BrPbevTechnicalSheetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.benchmark = load_inmetro_pbev_quantitative_benchmark(BENCHMARK_PATH)

    def test_publishes_source_native_pbev_facts_without_identity_matching_claim(self) -> None:
        sheets = publish_pbev_technical_sheets_from_benchmark(self.benchmark)
        self.assertEqual(4, len(sheets))

        mobi = next(sheet for sheet in sheets if sheet["vehicleId"] == "podium7:pbev:2026-p1-fiat-mobi-trekking")
        self.assertEqual(CONTRACT_SCHEMA, mobi["schema"])
        self.assertEqual("BR", mobi["source"]["market"])
        self.assertIn("do not participate", mobi["source"]["identityBoundary"])
        self.assertEqual(CONTRACT_FIELDS, {fact["field"] for fact in mobi["facts"]})

        facts = {fact["field"]: fact for fact in mobi["facts"]}
        self.assertEqual(
            {
                "field": "ethanol_city_consumption",
                "knowledgeState": "known",
                "provenanceRef": "inmetro:pbev:pbev-2026-p1-fiat-mobi-trekking:column:17",
                "rawValue": "9.8",
                "value": 9.8,
                "unit": "km/l",
            },
            facts["ethanol_city_consumption"],
        )
        self.assertEqual(
            {
                "field": "electric_range",
                "knowledgeState": "not_applicable",
                "provenanceRef": "inmetro:pbev:pbev-2026-p1-fiat-mobi-trekking:column:24",
                "rawValue": "\\",
                "reason": "source cell is the retained PBEV not-applicable placeholder",
            },
            facts["electric_range"],
        )

    def test_electric_vehicle_keeps_kmle_and_range_without_combined_consumption_inference(self) -> None:
        sheets = publish_pbev_technical_sheets_from_benchmark(self.benchmark)
        byd = next(sheet for sheet in sheets if sheet["vehicleId"] == "podium7:pbev:2026-p1-byd-dolphin-mini-gs-ev")
        facts = {fact["field"]: fact for fact in byd["facts"]}

        self.assertEqual(58.6, facts["electric_equivalent_city_efficiency"]["value"])
        self.assertEqual("km/le", facts["electric_equivalent_city_efficiency"]["unit"])
        self.assertEqual(280, facts["electric_range"]["value"])
        self.assertNotIn("fuel_economy_combined", facts)

    def test_publication_is_deterministic(self) -> None:
        first = publish_pbev_technical_sheets_from_benchmark(self.benchmark)
        second = publish_pbev_technical_sheets_from_benchmark(self.benchmark)

        self.assertEqual(first, second)
        encoded = json.dumps(first, ensure_ascii=False, sort_keys=True)
        self.assertIn("ethanol_road_consumption", encoded)

    def test_payload_requires_every_contract_field_exactly_once(self) -> None:
        with self.assertRaisesRegex(ValueError, "must cover every field"):
            publish_pbev_technical_sheet_payload(
                "podium7:pbev:test",
                [
                    PbevTechnicalSheetFact(
                        field="energy_consumption",
                        knowledge_state="known",
                        provenance_ref="inmetro:pbev:test:column:23",
                        raw_value="1.46",
                        value=1.46,
                        unit="MJ/km",
                    )
                ],
            )

    def test_not_applicable_facts_cannot_smuggle_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot carry"):
            PbevTechnicalSheetFact(
                field="electric_range",
                knowledge_state="not_applicable",
                provenance_ref="inmetro:pbev:test:column:24",
                raw_value="\\",
                value=123,
                unit="km",
                reason="placeholder",
            ).to_payload()


if __name__ == "__main__":
    unittest.main()
