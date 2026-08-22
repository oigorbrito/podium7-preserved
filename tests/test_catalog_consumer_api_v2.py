import unittest

from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_api import (
    CatalogApiErrorCode,
    list_catalog_vehicles,
    lookup_catalog_vehicle,
)


def vehicle(model: str) -> CatalogVehicleIdentity:
    return CatalogVehicleIdentity(make="Toyota", model=model, generation="G1")


class CatalogConsumerApiV2Tests(unittest.TestCase):
    def test_lookup_distinguishes_canonical_and_historical_requests(self) -> None:
        store = CatalogStore()
        survivor = store.create_catalog_vehicle(vehicle("Corolla"))
        duplicate = store.create_catalog_vehicle(vehicle("Corolla"))
        store.merge_catalog_vehicle_ids(survivor, duplicate)

        canonical = lookup_catalog_vehicle(store, survivor)
        historical = lookup_catalog_vehicle(store, duplicate)

        self.assertTrue(canonical["ok"])
        self.assertFalse(canonical["redirected"])
        self.assertEqual(canonical["requestedId"], survivor)
        self.assertEqual(canonical["canonicalId"], survivor)

        self.assertTrue(historical["ok"])
        self.assertTrue(historical["redirected"])
        self.assertEqual(historical["requestedId"], duplicate)
        self.assertEqual(historical["canonicalId"], survivor)
        self.assertEqual(historical["vehicle"]["entity"]["id"], survivor)
        self.assertEqual(historical["vehicle"]["redirectsFrom"], [duplicate])

    def test_unknown_lookup_returns_stable_not_found_error(self) -> None:
        store = CatalogStore()

        result = lookup_catalog_vehicle(store, "veh_missing")

        self.assertEqual(
            result,
            {
                "ok": False,
                "error": {
                    "code": CatalogApiErrorCode.NOT_FOUND.value,
                    "message": "catalog vehicle not found",
                    "requestedId": "veh_missing",
                },
            },
        )

    def test_list_uses_canonical_keyset_pagination_without_redirect_duplicates(self) -> None:
        store = CatalogStore()
        ids = [store.create_catalog_vehicle(vehicle(model)) for model in ("A", "B", "C", "D")]
        store.merge_catalog_vehicle_ids(ids[0], ids[1])
        expected = sorted((ids[0], ids[2], ids[3]))

        first = list_catalog_vehicles(store, limit=2)
        second = list_catalog_vehicles(store, limit=2, cursor=first["nextCursor"])

        self.assertTrue(first["ok"])
        self.assertEqual(len(first["items"]), 2)
        self.assertIsNotNone(first["nextCursor"])
        self.assertTrue(second["ok"])
        self.assertIsNone(second["nextCursor"])

        observed = [item["entity"]["id"] for item in first["items"] + second["items"]]
        self.assertEqual(observed, expected)
        self.assertNotIn(ids[1], observed)

    def test_invalid_inputs_return_explicit_error_codes(self) -> None:
        store = CatalogStore()
        store.create_catalog_vehicle(vehicle("Corolla"))

        cases = (
            (lookup_catalog_vehicle(store, ""), CatalogApiErrorCode.INVALID_ID),
            (list_catalog_vehicles(store, limit=0), CatalogApiErrorCode.INVALID_PAGE_SIZE),
            (list_catalog_vehicles(store, limit=101), CatalogApiErrorCode.INVALID_PAGE_SIZE),
            (list_catalog_vehicles(store, cursor="veh_missing"), CatalogApiErrorCode.INVALID_CURSOR),
            (
                lookup_catalog_vehicle(store, "veh_missing", contract_version="3.0"),
                CatalogApiErrorCode.UNSUPPORTED_CONTRACT_VERSION,
            ),
        )
        for result, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"]["code"], expected_code.value)


if __name__ == "__main__":
    unittest.main()
