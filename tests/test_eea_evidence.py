import hashlib
import json
import unittest
from datetime import datetime, timezone

from podium7.eea_evidence import parse_eea_evidence


class EeaEvidenceAdapterTests(unittest.TestCase):
    def _raw(self, *, variant="UZH4", version="UZH4VD01", capacity=1969):
        return json.dumps(
            {
                "results": [
                    {
                        "ID": 162744196,
                        "MS": "SE",
                        "Mk": "VOLVO",
                        "Cn": "XC60",
                        "Man": "VOLVO CAR CORPORATION",
                        "TAN": "E4*2007/46*1220*25",
                        "T": "U",
                        "Va": variant,
                        "Ve": version,
                        "M (kg)": 2150,
                        "Ec (cm3)": capacity,
                        "Ep (KW)": 186,
                        "Ft": "petrol/electric",
                        "Fm": "P",
                        "Year": 2025,
                        "Ewltp (g/km)": 23,
                        "Z (Wh/km)": 183,
                        "Status": "P",
                    }
                ]
            },
            separators=(",", ":"),
        ).encode()

    def _parse(self, raw):
        digest = hashlib.sha256(raw).hexdigest()
        return parse_eea_evidence(
            raw,
            locator="https://discodata.eea.europa.eu/sql?query=bounded",
            retrieved_at=datetime(2026, 8, 23, 17, 58, 6, tzinfo=timezone.utc),
            raw_content_ref=f"sha256:{digest}@data/raw/web/eea-v1/fixture.json",
            entity_candidate_ids={162744196: "candidate:volvo-xc60"},
        )

    def test_preserves_regulatory_identity_without_retail_promotion(self):
        record = self._parse(self._raw())[0]
        facts = {fact.attribute: fact.normalized_value for fact in record.facts}
        self.assertEqual("VOLVO", facts["make"])
        self.assertEqual("XC60", facts["model"])
        self.assertEqual("E4*2007/46*1220*25", facts["eea.type_approval_number"])
        self.assertEqual("UZH4", facts["eea.variant"])
        self.assertEqual("UZH4VD01", facts["eea.version"])
        self.assertEqual(2025, facts["eea.registration_year"])
        self.assertEqual("plug_in_hybrid", facts["fuel_type"])
        self.assertEqual(1969, facts["displacement"])
        self.assertEqual(186, facts["power"])
        self.assertNotIn("variant", facts)
        self.assertNotIn("model_year", facts)
        self.assertNotIn("manufacture_year", facts)
        self.assertNotIn("curb_weight", facts)

    def test_blank_regulatory_identifiers_are_absence_of_evidence(self):
        record = self._parse(self._raw(variant="", version=""))[0]
        attrs = {fact.attribute for fact in record.facts}
        self.assertNotIn("eea.variant", attrs)
        self.assertNotIn("eea.version", attrs)

    def test_content_address_must_match_exact_bytes(self):
        raw = self._raw()
        with self.assertRaisesRegex(ValueError, "exact EEA response bytes"):
            parse_eea_evidence(
                raw,
                locator="https://discodata.eea.europa.eu/sql?query=bounded",
                retrieved_at=datetime(2026, 8, 23, tzinfo=timezone.utc),
                raw_content_ref="sha256:" + "0" * 64 + "@fixture.json",
                entity_candidate_ids={162744196: "candidate:volvo-xc60"},
            )

    def test_missing_or_extra_candidate_binding_fails_closed(self):
        raw = self._raw()
        digest = hashlib.sha256(raw).hexdigest()
        common = dict(
            locator="https://discodata.eea.europa.eu/sql?query=bounded",
            retrieved_at=datetime(2026, 8, 23, tzinfo=timezone.utc),
            raw_content_ref=f"sha256:{digest}@fixture.json",
        )
        with self.assertRaisesRegex(ValueError, "missing entity candidate binding"):
            parse_eea_evidence(raw, entity_candidate_ids={999: "candidate:other"}, **common)
        with self.assertRaisesRegex(ValueError, "absent EEA records"):
            parse_eea_evidence(raw, entity_candidate_ids={162744196: "candidate:volvo", 999: "candidate:other"}, **common)


if __name__ == "__main__":
    unittest.main()
