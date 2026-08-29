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

    def _parse(self, raw):
        digest = hashlib.sha256(raw).hexdigest()
        return parse_nhtsa_decode_vin_values(
            raw,
            locator=build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 2011),
            raw_content_ref=f"sha256:{digest}@data/raw/nhtsa-vpic/example.json",
            retrieved_at=datetime(2026, 8, 25, tzinfo=timezone.utc),
            entity_candidate_id="candidate:bmw-x3-2011",
        )

    def test_parses_only_explicit_allowlisted_fields_and_preserves_hash(self):
        raw = self._raw()
        result = self._parse(raw)
        facts = {fact.attribute: fact for fact in result.facts}
        self.assertEqual(facts["make"].normalized_value, "BMW")
        self.assertEqual(facts["model"].normalized_value, "X3")
        self.assertEqual(facts["model_year"].normalized_value, 2011)
        self.assertEqual(facts["nhtsa.make_id"].normalized_value, 452)
        self.assertEqual(facts["nhtsa.model_id"].normalized_value, 1719)
        self.assertEqual(facts["nhtsa.trim"].normalized_value, "xDrive35i")
        self.assertEqual(
            facts["nhtsa.body_class"].normalized_value,
            "Sport Utility Vehicle [SUV]/Multipurpose Vehicle [MPV]",
        )
        self.assertNotIn("manufacture_year", facts)
        self.assertNotIn("variant", facts)
        self.assertNotIn("body_style", facts)
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(result.evidence.id, f"nhtsa-vpic:{digest}")
        self.assertEqual(
            result.evidence.raw_content_ref,
            f"sha256:{digest}@data/raw/nhtsa-vpic/example.json",
        )
        self.assertEqual(result.source_error_code, "6")

    def test_clean_and_partial_vin_codes_are_accepted_but_accuracy_errors_fail_closed(self):
        clean = self._parse(self._raw(ErrorCode="0", ErrorText="0 - VIN decoded clean"))
        self.assertEqual("0", clean.source_error_code)
        partial = self._parse(self._raw(ErrorCode="6", ErrorText="6 - Incomplete VIN"))
        self.assertEqual("6", partial.source_error_code)
        for error_code in ("11", "6,11", "6,8", "400", "6,7,11,400"):
            with self.subTest(error_code=error_code):
                with self.assertRaisesRegex(ValueError, "unsupported decode error code"):
                    self._parse(self._raw(ErrorCode=error_code, ErrorText="source warning"))

    def test_blank_optional_fields_are_absence_of_evidence(self):
        result = self._parse(self._raw(Trim="", BodyClass="", FuelTypePrimary=""))
        attributes = {fact.attribute for fact in result.facts}
        self.assertNotIn("nhtsa.trim", attributes)
        self.assertNotIn("nhtsa.body_class", attributes)
        self.assertNotIn("nhtsa.fuel_type_primary", attributes)

    def test_requires_minimum_identity_context(self):
        for field in ("Make", "Model", "ModelYear"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    self._parse(self._raw(**{field: ""}))

    def test_fails_closed_on_malformed_cardinality_and_types(self):
        valid_row = {
            "Make": "BMW",
            "Model": "X3",
            "ModelYear": "2011",
            "ErrorCode": "0",
        }
        invalid_payloads = [
            b"not-json",
            json.dumps({"Count": 0, "Results": []}).encode(),
            json.dumps({"Count": True, "Results": [valid_row]}).encode(),
            json.dumps(
                {
                    "Count": 1,
                    "Results": [
                        {"Make": "BMW", "Model": "X3", "ModelYear": "2011", "MakeID": "x", "ErrorCode": "0"}
                    ],
                }
            ).encode(),
        ]
        for raw in invalid_payloads:
            with self.subTest(raw=raw[:20]):
                with self.assertRaises(ValueError):
                    self._parse(raw)

    def test_raw_content_reference_must_match_exact_bytes(self):
        raw = self._raw()
        with self.assertRaisesRegex(ValueError, "digest does not match"):
            parse_nhtsa_decode_vin_values(
                raw,
                locator=build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 2011),
                raw_content_ref=f"sha256:{'0' * 64}@data/raw/nhtsa-vpic/example.json",
                retrieved_at=datetime(2026, 8, 25, tzinfo=timezone.utc),
                entity_candidate_id="candidate:bmw-x3-2011",
            )

    def test_locator_is_bounded_and_encodes_model_year_semantics(self):
        self.assertEqual(
            build_nhtsa_decode_vin_values_locator("5uxwx7c5*ba", 2011),
            "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/5UXWX7C5*BA?format=json&modelyear=2011",
        )
        for invalid_vin in ("", "bad vin", "5UXWX7C5IBA"):
            with self.subTest(vin=invalid_vin):
                with self.assertRaises(ValueError):
                    build_nhtsa_decode_vin_values_locator(invalid_vin, 2011)
        with self.assertRaises(ValueError):
            build_nhtsa_decode_vin_values_locator("5UXWX7C5*BA", 1980)


if __name__ == "__main__":
    unittest.main()
