import unittest

from podium7.catalog import (
    CATALOG_CONTRACT_DEFAULT_VERSION,
    CatalogStore,
    CatalogVehicleIdentity,
    ExternalIdentifier,
    export_catalog_vehicle_payload,
)


class CatalogJsonContractV2Tests(unittest.TestCase):
    def test_v2_payload_freezes_field_names_and_collection_shapes(self) -> None:
        store = CatalogStore()
        vehicle_id = store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Toyota",
                model="Corolla",
                generation="E210",
                body_style="sedan",
                aliases=("Corolla Altis",),
                engine_identifiers=("2ZR-FXE",),
                external_identifiers=(ExternalIdentifier("fipe", "004001-0"),),
            )
        )

        payload = export_catalog_vehicle_payload(store, vehicle_id)

        self.assertEqual(set(payload), {"contractVersion", "entity", "redirectsFrom"})
        self.assertEqual(
            set(payload["entity"]),
            {
                "id",
                "make",
                "model",
                "generation",
                "variant",
                "powertrain",
                "transmission",
                "body_style",
                "market",
                "manufacture_year_from",
                "manufacture_year_to",
                "model_year_from",
                "model_year_to",
                "aliases",
                "engine_identifiers",
                "external_identifiers",
            },
        )
        self.assertIsInstance(payload["entity"]["aliases"], list)
        self.assertIsInstance(payload["entity"]["engine_identifiers"], list)
        self.assertIsInstance(payload["entity"]["external_identifiers"], list)
        self.assertEqual(
            payload["entity"]["external_identifiers"],
            [{"namespace": "fipe", "value": "004001-0"}],
        )

    def test_optional_fields_are_present_as_null_and_collections_as_arrays(self) -> None:
        store = CatalogStore()
        vehicle_id = store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla")
        )

        entity = export_catalog_vehicle_payload(store, vehicle_id)["entity"]

        for field in (
            "generation",
            "variant",
            "powertrain",
            "transmission",
            "body_style",
            "market",
            "manufacture_year_from",
            "manufacture_year_to",
            "model_year_from",
            "model_year_to",
        ):
            self.assertIsNone(entity[field])
        self.assertEqual(entity["aliases"], [])
        self.assertEqual(entity["engine_identifiers"], [])
        self.assertEqual(entity["external_identifiers"], [])

    def test_v2_is_default_and_unsupported_versions_fail_explicitly(self) -> None:
        store = CatalogStore()
        vehicle_id = store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla")
        )

        payload = export_catalog_vehicle_payload(store, vehicle_id)
        self.assertEqual(CATALOG_CONTRACT_DEFAULT_VERSION, "2.0")
        self.assertEqual(payload["contractVersion"], "2.0")

        with self.assertRaises(ValueError):
            export_catalog_vehicle_payload(store, vehicle_id, contract_version="3.0")

    def test_historical_id_exports_canonical_id_and_redirects(self) -> None:
        store = CatalogStore()
        survivor = store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", generation="E210")
        )
        duplicate = store.create_catalog_vehicle(
            CatalogVehicleIdentity(make="Toyota", model="Corolla", generation="E210")
        )
        store.merge_catalog_vehicle_ids(survivor, duplicate)

        payload = export_catalog_vehicle_payload(store, duplicate)

        self.assertEqual(payload["entity"]["id"], survivor)
        self.assertEqual(payload["redirectsFrom"], [duplicate])


if __name__ == "__main__":
    unittest.main()
