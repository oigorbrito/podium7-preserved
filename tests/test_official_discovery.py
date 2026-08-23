import unittest

from podium7.official_discovery import (
    DISCOVERY_ROLE,
    FUELECONOMY_SOURCE_ID,
    NHTSA_VPIC_SOURCE_ID,
    build_fueleconomy_model_menu_locator,
    build_fueleconomy_options_menu_locator,
    build_nhtsa_models_locator,
    discover_fueleconomy_models,
    discover_fueleconomy_vehicle_options,
    discover_nhtsa_models,
)


class OfficialDiscoveryTests(unittest.TestCase):
    def test_nhtsa_models_preserve_ids_locator_and_nonproof_semantics(self):
        payload = {
            "Count": 2,
            "Message": "Response returned successfully",
            "SearchCriteria": "Make:Toyota | ModelYear:2025",
            "Results": [
                {"Make_ID": 448, "Make_Name": "Toyota", "Model_ID": 2208, "Model_Name": "Corolla"},
                {"Make_ID": 448, "Make_Name": "Toyota", "Model_ID": 2211, "Model_Name": "Prius"},
            ],
        }
        candidates = discover_nhtsa_models(payload, make="Toyota", model_year=2025)
        self.assertEqual([candidate.model for candidate in candidates], ["Corolla", "Prius"])
        self.assertEqual(candidates[0].source_id, NHTSA_VPIC_SOURCE_ID)
        self.assertEqual(candidates[0].source_make_id, 448)
        self.assertEqual(candidates[0].source_model_id, 2208)
        self.assertEqual(candidates[0].evidence_role, DISCOVERY_ROLE)
        self.assertFalse(candidates[0].identity_proof)
        self.assertEqual(
            candidates[0].source_locator,
            "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/Toyota/modelyear/2025?format=json",
        )

    def test_nhtsa_duplicate_identical_model_id_is_deduplicated(self):
        row = {"Make_ID": 448, "Make_Name": "Toyota", "Model_ID": 2208, "Model_Name": "Corolla"}
        candidates = discover_nhtsa_models({"Count": 2, "Results": [row, dict(row)]}, make="Toyota", model_year=2025)
        self.assertEqual(len(candidates), 1)

    def test_nhtsa_conflicting_duplicate_fails(self):
        payload = {
            "Count": 2,
            "Results": [
                {"Make_ID": 448, "Make_Name": "Toyota", "Model_ID": 2208, "Model_Name": "Corolla"},
                {"Make_ID": 448, "Make_Name": "Toyota", "Model_ID": 2208, "Model_Name": "Different"},
            ],
        }
        with self.assertRaisesRegex(ValueError, "conflicting records"):
            discover_nhtsa_models(payload, make="Toyota", model_year=2025)

    def test_nhtsa_rejects_count_mismatch_make_mismatch_and_malformed_ids(self):
        with self.assertRaisesRegex(ValueError, "Count"):
            discover_nhtsa_models({"Count": 2, "Results": []}, make="Toyota", model_year=2025)
        with self.assertRaisesRegex(ValueError, "does not match"):
            discover_nhtsa_models(
                {"Count": 1, "Results": [{"Make_ID": 448, "Make_Name": "Lexus", "Model_ID": 1, "Model_Name": "RX"}]},
                make="Toyota",
                model_year=2025,
            )
        with self.assertRaisesRegex(ValueError, "Model_ID"):
            discover_nhtsa_models(
                {"Count": 1, "Results": [{"Make_ID": 448, "Make_Name": "Toyota", "Model_ID": "x", "Model_Name": "Corolla"}]},
                make="Toyota",
                model_year=2025,
            )

    def test_fueleconomy_model_menu_accepts_list_and_singleton(self):
        list_payload = {
            "menuItem": [
                {"text": "4Runner 2WD", "value": "4Runner 2WD"},
                {"text": "bZ4X", "value": "bZ4X"},
            ]
        }
        candidates = discover_fueleconomy_models(list_payload, make="Toyota", model_year=2025)
        self.assertEqual({candidate.model for candidate in candidates}, {"4Runner 2WD", "bZ4X"})
        self.assertTrue(all(candidate.source_id == FUELECONOMY_SOURCE_ID for candidate in candidates))
        self.assertTrue(all(not candidate.identity_proof for candidate in candidates))

        singleton = discover_fueleconomy_models(
            {"menuItem": {"text": "bZ4X", "value": "bZ4X"}}, make="Toyota", model_year=2025
        )
        self.assertEqual(len(singleton), 1)
        self.assertEqual(singleton[0].source_model_key, "bZ4X")

    def test_fueleconomy_model_duplicate_handling_is_fail_closed(self):
        duplicate = {"menuItem": [{"text": "bZ4X", "value": "bZ4X"}, {"text": "bZ4X", "value": "bZ4X"}]}
        self.assertEqual(len(discover_fueleconomy_models(duplicate, make="Toyota", model_year=2025)), 1)
        conflict = {"menuItem": [{"text": "bZ4X", "value": "same"}, {"text": "Other", "value": "same"}]}
        with self.assertRaisesRegex(ValueError, "conflicting records"):
            discover_fueleconomy_models(conflict, make="Toyota", model_year=2025)

    def test_fueleconomy_options_yield_vehicle_ids_without_identity_claim(self):
        payload = {
            "menuItem": [
                {"text": "Corolla 2.0 L, 4 cyl, Automatic (AV-S10)", "value": "47755"},
                {"text": "Corolla 2.0 L, 4 cyl, Manual 6-spd", "value": "47756"},
            ]
        }
        candidates = discover_fueleconomy_vehicle_options(
            payload, make="Toyota", model="Corolla", model_year=2025
        )
        self.assertEqual([candidate.source_vehicle_id for candidate in candidates], [47755, 47756])
        self.assertEqual(candidates[0].model, "Corolla")
        self.assertEqual(candidates[0].source_model_key, "Corolla")
        self.assertFalse(candidates[0].identity_proof)
        self.assertIn("menu/options", candidates[0].source_locator)

    def test_fueleconomy_options_reject_non_numeric_vehicle_id_and_conflicts(self):
        with self.assertRaisesRegex(ValueError, "positive integer"):
            discover_fueleconomy_vehicle_options(
                {"menuItem": {"text": "one", "value": "not-an-id"}},
                make="Toyota",
                model="Corolla",
                model_year=2025,
            )
        conflict = {"menuItem": [{"text": "one", "value": "1"}, {"text": "two", "value": "1"}]}
        with self.assertRaisesRegex(ValueError, "conflicting records"):
            discover_fueleconomy_vehicle_options(
                conflict, make="Toyota", model="Corolla", model_year=2025
            )

    def test_fueleconomy_rejects_missing_or_malformed_menu(self):
        for payload in ({}, {"menuItem": None}, {"menuItem": ["bad"]}):
            with self.assertRaises(ValueError):
                discover_fueleconomy_models(payload, make="Toyota", model_year=2025)

    def test_locator_builders_encode_inputs_and_validate_year_boundaries(self):
        self.assertEqual(
            build_nhtsa_models_locator("Mercedes-Benz", 2025),
            "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/Mercedes-Benz/modelyear/2025?format=json",
        )
        self.assertEqual(
            build_fueleconomy_model_menu_locator("Land Rover", 2025),
            "https://www.fueleconomy.gov/ws/rest/vehicle/menu/model?year=2025&make=Land+Rover",
        )
        self.assertEqual(
            build_fueleconomy_options_menu_locator("Land Rover", "Range Rover", 2025),
            "https://www.fueleconomy.gov/ws/rest/vehicle/menu/options?year=2025&make=Land+Rover&model=Range+Rover",
        )
        with self.assertRaises(ValueError):
            build_nhtsa_models_locator("Toyota", 1995)
        with self.assertRaises(ValueError):
            build_fueleconomy_model_menu_locator("Toyota", 1983)


if __name__ == "__main__":
    unittest.main()
