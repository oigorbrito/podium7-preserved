import hashlib
import json
import unittest
from datetime import datetime, timezone

from podium7.nhtsa_vpic_evidence import (
    build_nhtsa_decode_vin_values_locator,
    parse_nhtsa_decode_vin_values,
)


class NhtsaVpicEvidenceTests(unittest.TestCase):
    def _raw(self, **updates):
        row = {
            "Make": "BMW",
            "MakeID": "452",
            "Model": "X3",
            "ModelID": "1719",
            "ModelYear": "2011",
            "BodyClass": "Sport Utility Vehicle [SUV]/Multipurpose Vehicle [MPV]",
            "Trim": "xDrive35i",
            "Series": "",
            "EngineModel": "",
            "TransmissionStyle": "",
            "FuelTypePrimary": "Gasoline",
            "DriveType": "AWD/All-Wheel Drive",
            "ErrorCode": "6",
            "ErrorText": "6 - Incomplete VIN",
        }
        row.update(updates)
        return json.dumps(
            {
                "Count": 1,
                "Message": (
                    "Results returned successfully. NOTE: Any missing decoded values should be interpreted "
                    "as NHTSA does not have data on the specific variable. Missing value should NOT be "
                    "interpreted as an indication that a feature or technology is unavailable for a vehicle."
                ),
                "SearchCriteria": "VIN(s): 5UXWX7C5*BA",
                "Results": [row],
            },
            separators=(",", ":"),
        ).encode("utf-8")

    def test_parses_only_explicit_allowlisted_fields_and_preserves_hash(self):
        raw = self._raw()
        locator = build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 2011)
        result = parse_nhtsa_decode_vin_values(
            raw,
            locator=locator,
            retrieved_at=datetime(2026, 8, 25, tzinfo=timezone.utc),
            entity_candidate_id="candidate:bmw-x3-2011",
        )
        facts = {fact.attribute: fact for fact in result.facts}
        self.assertEqual(facts["make"].normalized_value, "BMW")
        self.assertEqual(facts["model"].normalized_value, "X3")
        self.assertEqual(facts["model_year"].normalized_value, 2011)
        self.assertEqual(facts["nhtsa.make_id"].normalized_value, 452)
        self.assertEqual(facts["nhtsa.model_id"].normalized_value, 1719)
        self.assertEqual(facts["nhtsa.trim"].normalized_value, "xDrive35i")
        self.assertEqual(facts["nhtsa.body_class"].normalized_value, "Sport Utility Vehicle [SUV]/Multipurpose Vehicle [MPV]")
        self.assertNotIn("manufacture_year", facts)
        self.assertNotIn("variant", facts)
        self.assertNotIn("body_style", facts)
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(result.evidence.id, f"nhtsa-vpic:{digest}")
        self.assertEqual(result.evidence.raw_content_ref, f"sha256:{digest}@{locator}")
        self.assertEqual(result.source_error_code, "6")

    def test_blank_optional_fields_are_absence_of_evidence(self):
        result = parse_nhtsa_decode_vin_values(
            self._raw(Trim="", BodyClass="", FuelTypePrimary=""),
            locator=build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 2011),
            retrieved_at=datetime(2026, 8, 25, tzinfo=timezone.utc),
            entity_candidate_id="candidate:bmw-x3-2011",
        )
        attributes = {fact.attribute for fact in result.facts}
        self.assertNotIn("nhtsa.trim", attributes)
        self.assertNotIn("nhtsa.body_class", attributes)
        self.assertNotIn("nhtsa.fuel_type_primary", attributes)

    def test_requires_minimum_identity_context(self):
        for field in ("Make", "Model", "ModelYear"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    parse_nhtsa_decode_vin_values(
                        self._raw(**{field: ""}),
                        locator=build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 2011),
                        retrieved_at=datetime(2026, 8, 25, tzinfo=timezone.utc),
                        entity_candidate_id="candidate:bmw-x3-2011",
                    )

    def test_fails_closed_on_malformed_cardinality_and_types(self):
        invalid_payloads = [
            b"not-json",
            json.dumps({"Count": 0, "Results": []}).encode(),
            json.dumps({"Count": 1, "Results": [{"Make": "BMW", "Model": "X3", "ModelYear": "2011", "MakeID": "x"}]}).encode(),
        ]
        for raw in invalid_payloads:
            with self.subTest(raw=raw[:20]):
                with self.assertRaises(ValueError):
                    parse_nhtsa_decode_vin_values(
                        raw,
                        locator=build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 2011),
                        retrieved_at=datetime(2026, 8, 25, tzinfo=timezone.utc),
                        entity_candidate_id="candidate:bmw-x3-2011",
                    )

    def test_locator_is_bounded_and_encodes_model_year_semantics(self):
        self.assertEqual(
            build_nhtsa_decode_vin_values_locator("5uxwx7c5*ba", 2011),
            "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/5UXWX7C5*BA?format=json&modelyear=2011",
        )
        with self.assertRaises(ValueError):
            build_nhtsa_decode_vin_values_locator("", 2011)
        with self.assertRaises(ValueError):
            build_nhtsa_decode_vin_values_locator("bad vin", 2011)
        with self.assertRaises(ValueError):
            build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 1980)


if __name__ == "__main__":
    unittest.main()
