import json
import unittest
from pathlib import Path


class InmetroPbevQuantitativeSemanticObservationTests(unittest.TestCase):
    def setUp(self):
        path = Path("benchmarks/inmetro_pbev_quantitative_semantics_observation_v1.json")
        self.payload = json.loads(path.read_text(encoding="utf-8"))

    def test_live_observation_cannot_satisfy_source_bound_acceptance(self):
        self.assertEqual("LIVE_SOURCE_OBSERVATION_NOT_ACCEPTANCE", self.payload["status"])
        self.assertFalse(self.payload["acceptanceGuard"]["sourceBoundAcceptanceAllowed"])
        self.assertIsNone(self.payload["source"]["rawContentSha256"])
        self.assertIsNone(self.payload["source"]["snapshotLocator"])
        self.assertEqual("LIVE_MUTABLE_SOURCE_ONLY", self.payload["source"]["snapshotRetrievability"])

    def test_observed_quantities_keep_source_units_and_identity_boundary(self):
        fields = self.payload["fields"]
        self.assertEqual("MJ/km", fields["energy_consumption"]["sourceUnit"])
        self.assertEqual("km", fields["electric_range"]["sourceUnit"])
        self.assertEqual(["fuel"], fields["fuel_consumption_city"]["requiredContext"])
        self.assertEqual(["fuel"], fields["fuel_consumption_highway"]["requiredContext"])
        self.assertFalse(self.payload["identityBoundary"]["quantitativeFactsParticipateInIdentityResolution"])

    def test_unproven_column_semantics_fail_closed(self):
        fields = self.payload["fields"]
        self.assertEqual("BLOCKED_PENDING_SOURCE_BOUND_HEADER_CONTEXT", fields["fuel_consumption_city"]["status"])
        self.assertEqual("BLOCKED_PENDING_SOURCE_BOUND_HEADER_CONTEXT", fields["fuel_consumption_highway"]["status"])
        self.assertEqual("BLOCKED_PENDING_EXACT_COLUMN_SEMANTICS", fields["co2_fossil"]["status"])
        self.assertEqual("BLOCKED_PENDING_EXACT_COLUMN_SEMANTICS", fields["co2e_fossil"]["status"])
        self.assertEqual({"ND", "N.A."}, set(self.payload["missingMarkersObserved"]))

    def test_retained_observation_cases_do_not_infer_fuel_context(self):
        cases = {case["id"]: case for case in self.payload["cases"]}
        byd = cases["pbev-current-p1-byd-dolphin-mini-gs-ev"]
        self.assertEqual({"value": 0.41, "unit": "MJ/km"}, byd["observedQuantities"]["energy_consumption"])
        self.assertEqual({"value": 280, "unit": "km"}, byd["observedQuantities"]["electric_range"])

        mobi = cases["pbev-current-p1-fiat-mobi-trekking"]
        self.assertEqual({"value": 1.46, "unit": "MJ/km"}, mobi["observedQuantities"]["energy_consumption"])
        self.assertTrue(mobi["unboundObservations"]["fuelConsumptionValuesPresent"])
        self.assertNotIn("fuel_consumption_city", mobi["observedQuantities"])
        self.assertNotIn("fuel_consumption_highway", mobi["observedQuantities"])


if __name__ == "__main__":
    unittest.main()
