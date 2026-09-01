from __future__ import annotations

from copy import deepcopy
import unittest

from podium7.catalog_operational_v2 import (
    CATALOG_OPERATIONAL_V2,
    DUPLICATE_EVIDENCE_ID,
    DUPLICATE_FIELD_EVIDENCE,
    DUPLICATE_SOURCE_ID,
    EMPTY_FIELD_EVIDENCE,
    EXTRANEOUS_FIELD_EVIDENCE,
    INVALID_RECORD_ID,
    INVALID_VEHICLE,
    MISSING_FIELD_EVIDENCE,
    UNKNOWN_EVIDENCE_SOURCE,
    UNKNOWN_FIELD_EVIDENCE,
    UNSUPPORTED_CONTRACT_VERSION,
    CatalogOperationalV2Error,
    parse_catalog_operational_v2,
)


class CatalogOperationalV2Tests(unittest.TestCase):
    def _payload(self) -> dict:
        return {
            "contractVersion": CATALOG_OPERATIONAL_V2,
            "recordId": "br:t-cross:highline",
            "vehicle": {
                "make": "Volkswagen",
                "model": "T-Cross",
                "generation": "2019 Brazil generation",
                "variant": "Highline 250 TSI",
                "powertrain": "250 TSI flex",
                "transmission": "6-speed automatic",
                "market": "BR",
            },
            "provenance": {
                "sources": [
                    {
                        "id": "vw-generation",
                        "name": "Volkswagen generation source",
                        "locator": "https://example.test/generation",
                    },
                    {
                        "id": "vw-configuration",
                        "name": "Volkswagen configuration source",
                        "locator": "https://example.test/configuration",
                    },
                ],
                "evidence": [
                    {
                        "id": "ev-generation",
                        "sourceId": "vw-generation",
                        "locator": "https://example.test/generation/t-cross",
                        "retrievedAt": "2026-08-31T12:00:00+00:00",
                        "acquisitionMethod": "fixture",
                        "rawContentRef": "fixture:generation",
                    },
                    {
                        "id": "ev-configuration",
                        "sourceId": "vw-configuration",
                        "locator": "https://example.test/configuration/t-cross",
                        "retrievedAt": "2026-08-31T12:00:00+00:00",
                        "acquisitionMethod": "fixture",
                        "rawContentRef": "fixture:configuration",
                    },
                ],
                "fieldEvidence": {
                    "make": ["ev-configuration", "ev-generation"],
                    "model": ["ev-generation", "ev-configuration"],
                    "generation": ["ev-generation"],
                    "variant": ["ev-configuration"],
                    "powertrain": ["ev-configuration"],
                    "transmission": ["ev-configuration"],
                    "market": ["ev-generation", "ev-configuration"],
                },
            },
        }

    def _assert_code(self, payload: dict, code: str) -> None:
        with self.assertRaises(CatalogOperationalV2Error) as captured:
            parse_catalog_operational_v2(payload)
        self.assertEqual(captured.exception.code, code)

    def test_valid_composite_normalizes_independent_of_input_order(self) -> None:
        forward_payload = self._payload()
        reverse_payload = deepcopy(forward_payload)
        reverse_payload["provenance"]["sources"].reverse()
        reverse_payload["provenance"]["evidence"].reverse()
        for refs in reverse_payload["provenance"]["fieldEvidence"].values():
            refs.reverse()

        forward = parse_catalog_operational_v2(forward_payload)
        reverse = parse_catalog_operational_v2(reverse_payload)

        self.assertEqual(forward, reverse)
        self.assertEqual(
            tuple(source.id for source in forward.sources),
            ("vw-configuration", "vw-generation"),
        )
        self.assertEqual(
            tuple(evidence.id for evidence in forward.evidence),
            ("ev-configuration", "ev-generation"),
        )
        self.assertEqual(
            forward.field_evidence_map["make"],
            ("ev-configuration", "ev-generation"),
        )

    def test_unsupported_version_fails_closed(self) -> None:
        payload = self._payload()
        payload["contractVersion"] = "podium7.catalog-operational.v3"
        self._assert_code(payload, UNSUPPORTED_CONTRACT_VERSION)

    def test_empty_record_id_fails_closed(self) -> None:
        payload = self._payload()
        payload["recordId"] = "  "
        self._assert_code(payload, INVALID_RECORD_ID)

    def test_invalid_vehicle_fails_closed(self) -> None:
        payload = self._payload()
        payload["vehicle"]["not_a_catalog_field"] = "value"
        self._assert_code(payload, INVALID_VEHICLE)

    def test_duplicate_source_id_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["sources"][1]["id"] = "vw-generation"
        self._assert_code(payload, DUPLICATE_SOURCE_ID)

    def test_duplicate_evidence_id_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["evidence"][1]["id"] = "ev-generation"
        self._assert_code(payload, DUPLICATE_EVIDENCE_ID)

    def test_unknown_evidence_source_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["evidence"][0]["sourceId"] = "undeclared-source"
        self._assert_code(payload, UNKNOWN_EVIDENCE_SOURCE)

    def test_missing_present_field_binding_fails_closed(self) -> None:
        payload = self._payload()
        del payload["provenance"]["fieldEvidence"]["generation"]
        self._assert_code(payload, MISSING_FIELD_EVIDENCE)

    def test_extraneous_absent_field_binding_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["fieldEvidence"]["body_style"] = ["ev-configuration"]
        self._assert_code(payload, EXTRANEOUS_FIELD_EVIDENCE)

    def test_empty_field_binding_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["fieldEvidence"]["generation"] = []
        self._assert_code(payload, EMPTY_FIELD_EVIDENCE)

    def test_unknown_field_evidence_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["fieldEvidence"]["generation"] = ["unknown-evidence"]
        self._assert_code(payload, UNKNOWN_FIELD_EVIDENCE)

    def test_duplicate_field_evidence_fails_closed(self) -> None:
        payload = self._payload()
        payload["provenance"]["fieldEvidence"]["generation"] = [
            "ev-generation",
            "ev-generation",
        ]
        self._assert_code(payload, DUPLICATE_FIELD_EVIDENCE)


if __name__ == "__main__":
    unittest.main()
