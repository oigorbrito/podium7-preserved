from __future__ import annotations

import json
from pathlib import Path
import unittest

from podium7.eea_source import EEA_RETAIL_IDENTITY_PROOF, extract_eea_record_report


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmarks" / "eea_semantic_expansion_v2.json"


def _row(fuel_type: str, fuel_mode: str) -> dict[str, object]:
    return {
        "ID": 900001,
        "MS": "DE",
        "Mk": "TEST",
        "Cn": "TEST MODEL",
        "Man": "TEST MANUFACTURER",
        "TAN": "e1*2018/858*0001*00",
        "T": "AAA",
        "Va": "V1",
        "Ve": "E1",
        "Year": 2025,
        "Status": "Provisional",
        "M (kg)": 1600,
        "Ec (cm3)": 1995,
        "Ep (KW)": 110,
        "Ft": fuel_type,
        "Fm": fuel_mode,
        "Ewltp (g/km)": 120,
        "Z (Wh/km)": None,
    }


class EeaSemanticExpansionTests(unittest.TestCase):
    def test_official_classification_benchmark_is_fully_supported(self) -> None:
        payload = json.loads(BENCHMARK.read_text(encoding="utf-8"))
        self.assertFalse(payload["retailIdentityProof"])
        self.assertFalse(EEA_RETAIL_IDENTITY_PROOF)
        for case in payload["cases"]:
            report = extract_eea_record_report(_row(case["fuelType"], case["fuelMode"]))
            self.assertEqual((), report.issues)
            facts = {fact.attribute: fact.normalized_value for fact in report.facts}
            self.assertEqual(case["expected"], facts["fuel_type"])

    def test_unknown_diesel_combination_still_fails_closed(self) -> None:
        report = extract_eea_record_report(_row("diesel/electric", "X"))
        self.assertIn("UNSUPPORTED_FUEL_SEMANTICS", [issue.code for issue in report.issues])
        self.assertNotIn("fuel_type", {fact.attribute for fact in report.facts})

    def test_regulatory_type_variant_version_do_not_become_retail_identity_proof(self) -> None:
        report = extract_eea_record_report(_row("diesel", "M"))
        self.assertEqual("AAA", report.identity.vehicle_type)
        self.assertEqual("V1", report.identity.variant)
        self.assertEqual("E1", report.identity.version)
        self.assertFalse(EEA_RETAIL_IDENTITY_PROOF)


if __name__ == "__main__":
    unittest.main()
