import copy
import unittest

from podium7.catalog_multisource_v2 import (
    CATALOG_MULTISOURCE_V2_CONTRACT,
    CatalogMultisourceV2Error,
    parse_catalog_multisource_v2_record,
)


def valid_payload() -> dict[str, object]:
    return {
        "contractVersion": CATALOG_MULTISOURCE_V2_CONTRACT,
        "recordId": "example:t-cross:highline",
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
                    "id": "source-generation",
                    "name": "Generation source",
                    "locator": "https://example.test/generation",
                },
                {
                    "id": "source-configuration",
                    "name": "Configuration source",
                    "locator": "https://example.test/configuration",
                },
            ],
            "evidence": [
                {
                    "id": "evidence-generation",
                    "sourceId": "source-generation",
                    "locator": "https://example.test/generation/t-cross",
                    "retrievedAt": "2026-08-31T12:00:00+00:00",
                    "acquisitionMethod": "fixture",
                    "rawContentRef": "fixture:generation",
                },
                {
                    "id": "evidence-configuration",
                    "sourceId": "source-configuration",
                    "locator": "https://example.test/configuration/t-cross",
                    "retrievedAt": "2026-08-31T12:00:00+00:00",
                    "acquisitionMethod": "fixture",
                    "rawContentRef": "fixture:configuration",
                },
            ],
            "fieldEvidence": {
                "make": ["evidence-generation", "evidence-configuration"],
                "model": ["evidence-generation", "evidence-configuration"],
                "generation": ["evidence-generation"],
                "variant": ["evidence-configuration"],
                "powertrain": ["evidence-configuration"],
                "transmission": ["evidence-configuration"],
                "market": ["evidence-generation", "evidence-configuration"],
            },
        },
    }


class CatalogMultisourceV2Tests(unittest.TestCase):
    def assert_code(self, payload: object, expected: str) -> None:
        with self.assertRaises(CatalogMultisourceV2Error) as raised:
            parse_catalog_multisource_v2_record(payload)
        self.assertEqual(raised.exception.code, expected)

    def test_valid_two_source_payload_preserves_field_bindings(self) -> None:
        envelope = parse_catalog_multisource_v2_record(valid_payload())
        self.assertEqual(envelope.record_id, "example:t-cross:highline")
        self.assertEqual(
            tuple(source.id for source in envelope.sources),
            ("source-configuration", "source-generation"),
        )
        self.assertEqual(
            envelope.evidence_ids_for_field("variant"),
            ("evidence-configuration",),
        )
        self.assertEqual(
            envelope.evidence_ids_for_field("make"),
            ("evidence-configuration", "evidence-generation"),
        )

    def test_equivalent_input_order_normalizes_identically(self) -> None:
        forward = valid_payload()
        reverse = copy.deepcopy(forward)
        provenance = reverse["provenance"]
        assert isinstance(provenance, dict)
        provenance["sources"] = list(reversed(provenance["sources"]))
        provenance["evidence"] = list(reversed(provenance["evidence"]))
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        for field_name, refs in tuple(field_evidence.items()):
            field_evidence[field_name] = list(reversed(refs))

        self.assertEqual(
            parse_catalog_multisource_v2_record(forward),
            parse_catalog_multisource_v2_record(reverse),
        )

    def test_unsupported_contract_version_fails_closed(self) -> None:
        payload = valid_payload()
        payload["contractVersion"] = "podium7.catalog-operational.v999"
        self.assert_code(payload, "UNSUPPORTED_CONTRACT_VERSION")

    def test_empty_record_id_fails_closed(self) -> None:
        payload = valid_payload()
        payload["recordId"] = "   "
        self.assert_code(payload, "INVALID_RECORD_ID")

    def test_duplicate_source_id_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        sources = provenance["sources"]
        assert isinstance(sources, list)
        sources[1]["id"] = sources[0]["id"]
        self.assert_code(payload, "DUPLICATE_SOURCE_ID")

    def test_duplicate_evidence_id_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        evidence = provenance["evidence"]
        assert isinstance(evidence, list)
        evidence[1]["id"] = evidence[0]["id"]
        self.assert_code(payload, "DUPLICATE_EVIDENCE_ID")

    def test_unknown_evidence_source_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        evidence = provenance["evidence"]
        assert isinstance(evidence, list)
        evidence[0]["sourceId"] = "source-missing"
        self.assert_code(payload, "UNKNOWN_EVIDENCE_SOURCE")

    def test_missing_present_field_binding_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        del field_evidence["transmission"]
        self.assert_code(payload, "MISSING_FIELD_EVIDENCE")

    def test_extraneous_field_binding_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        field_evidence["body_style"] = ["evidence-configuration"]
        self.assert_code(payload, "EXTRANEOUS_FIELD_EVIDENCE")

    def test_empty_field_binding_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        field_evidence["variant"] = []
        self.assert_code(payload, "EMPTY_FIELD_EVIDENCE")

    def test_unknown_field_evidence_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        field_evidence["variant"] = ["evidence-missing"]
        self.assert_code(payload, "UNKNOWN_FIELD_EVIDENCE")

    def test_duplicate_field_evidence_fails_closed(self) -> None:
        payload = valid_payload()
        provenance = payload["provenance"]
        assert isinstance(provenance, dict)
        field_evidence = provenance["fieldEvidence"]
        assert isinstance(field_evidence, dict)
        field_evidence["variant"] = ["evidence-configuration", "evidence-configuration"]
        self.assert_code(payload, "DUPLICATE_FIELD_EVIDENCE")

    def test_invalid_vehicle_uses_existing_identity_contract(self) -> None:
        payload = valid_payload()
        vehicle = payload["vehicle"]
        assert isinstance(vehicle, dict)
        vehicle["unsupported"] = "value"
        self.assert_code(payload, "INVALID_VEHICLE")


if __name__ == "__main__":
    unittest.main()
