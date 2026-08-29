from pathlib import Path
import unittest

from podium7.enrichment_contract import (
    CONTRACT_SCHEMA,
    KnowledgeState,
    PublishedEnrichmentConflict,
    PublishedEnrichmentFact,
    ValueShape,
    publish_enrichment_json,
    publish_enrichment_payload,
)
from podium7.web_extraction import AUTOEVOLUTION_ARTEGA_GT_RULES_V2, extract_with_rules_report


ROOT = Path(__file__).resolve().parents[1]
RANGE_SOURCE = ROOT / "data/raw/web/corpus-v1/autoevolution-toyota-corolla-cross-2025-2.0-awd-169hp-range-weight.txt"
RANGE_SOURCE_PROVENANCE = "git:blob:514ba9e738607376551f71e7f650af42686e68ea"


class EnrichmentContractTests(unittest.TestCase):
    def test_retained_curb_weight_range_publishes_with_unit_and_provenance(self) -> None:
        report = extract_with_rules_report(
            RANGE_SOURCE.read_text(encoding="utf-8"),
            AUTOEVOLUTION_ARTEGA_GT_RULES_V2,
        )
        curb_weight = next(fact for fact in report.facts if fact.attribute == "curb_weight")

        payload = publish_enrichment_payload(
            "podium7:vehicle:toyota-corolla-cross-2025-2.0-awd",
            [
                PublishedEnrichmentFact(
                    field="curb_weight",
                    knowledge_state=KnowledgeState.KNOWN,
                    value_shape=ValueShape.RANGE,
                    value=curb_weight.normalized_value,
                    unit=curb_weight.unit,
                    provenance_ref=RANGE_SOURCE_PROVENANCE,
                )
            ],
        )

        self.assertEqual(payload["schema"], CONTRACT_SCHEMA)
        self.assertEqual(payload["vehicleId"], "podium7:vehicle:toyota-corolla-cross-2025-2.0-awd")
        self.assertEqual(len(payload["revision"]), 64)
        self.assertEqual(
            payload["facts"],
            [
                {
                    "field": "curb_weight",
                    "knowledgeState": "known",
                    "provenanceRef": RANGE_SOURCE_PROVENANCE,
                    "valueShape": "range",
                    "value": {"minValue": 1490, "maxValue": 1508},
                    "unit": "kg",
                }
            ],
        )
        self.assertEqual(payload["conflicts"], [])

    def test_unknown_state_is_explicit_and_deterministic(self) -> None:
        fact = PublishedEnrichmentFact(
            field="torque",
            knowledge_state=KnowledgeState.UNKNOWN,
            provenance_ref="publication:vehicle:torque:unknown",
        )

        first = publish_enrichment_json("podium7:vehicle:1", [fact], indent=None)
        second = publish_enrichment_json("podium7:vehicle:1", [fact], indent=None)

        self.assertEqual(first, second)
        self.assertIn('"knowledgeState": "unknown"', first)

    def test_fact_order_does_not_change_revision_or_payload(self) -> None:
        first = PublishedEnrichmentFact(
            field="power",
            knowledge_state=KnowledgeState.KNOWN,
            value_shape=ValueShape.SCALAR,
            value=169,
            unit="hp",
            provenance_ref="raw:web:power",
        )
        second = PublishedEnrichmentFact(
            field="curb_weight",
            knowledge_state=KnowledgeState.KNOWN,
            value_shape=ValueShape.RANGE,
            value={"minValue": 1490, "maxValue": 1508},
            unit="kg",
            provenance_ref="raw:web:weight",
        )

        a = publish_enrichment_payload("podium7:vehicle:1", [first, second])
        b = publish_enrichment_payload("podium7:vehicle:1", [second, first])

        self.assertEqual(a, b)

    def test_correction_changes_revision_but_preserves_vehicle_identity(self) -> None:
        before = publish_enrichment_payload(
            "podium7:vehicle:1",
            [
                PublishedEnrichmentFact(
                    field="power",
                    knowledge_state=KnowledgeState.KNOWN,
                    value_shape=ValueShape.SCALAR,
                    value=169,
                    unit="hp",
                    provenance_ref="raw:web:power:v1",
                )
            ],
        )
        after = publish_enrichment_payload(
            "podium7:vehicle:1",
            [
                PublishedEnrichmentFact(
                    field="power",
                    knowledge_state=KnowledgeState.KNOWN,
                    value_shape=ValueShape.SCALAR,
                    value=170,
                    unit="hp",
                    provenance_ref="raw:web:power:v2",
                )
            ],
        )

        self.assertEqual(before["vehicleId"], after["vehicleId"])
        self.assertNotEqual(before["revision"], after["revision"])

    def test_unresolved_conflict_is_explicit_and_blocks_same_field_fact(self) -> None:
        conflict = PublishedEnrichmentConflict(
            field="power",
            provenance_refs=("source:a", "source:b"),
            reason="retained sources disagree",
        )
        payload = publish_enrichment_payload("podium7:vehicle:1", [], [conflict])

        self.assertEqual(payload["facts"], [])
        self.assertEqual(
            payload["conflicts"],
            [
                {
                    "field": "power",
                    "provenanceRefs": ["source:a", "source:b"],
                    "reason": "retained sources disagree",
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, "blocks canonical publication"):
            publish_enrichment_payload(
                "podium7:vehicle:1",
                [
                    PublishedEnrichmentFact(
                        field="power",
                        knowledge_state=KnowledgeState.KNOWN,
                        value_shape=ValueShape.SCALAR,
                        value=169,
                        unit="hp",
                        provenance_ref="source:a",
                    )
                ],
                [conflict],
            )

    def test_quantitative_known_fact_requires_unit(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires unit"):
            PublishedEnrichmentFact(
                field="curb_weight",
                knowledge_state=KnowledgeState.KNOWN,
                value_shape=ValueShape.SCALAR,
                value=1500,
                provenance_ref="raw:web:weight",
            ).to_payload()

    def test_quantitative_scalar_requires_numeric_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "numeric"):
            PublishedEnrichmentFact(
                field="power",
                knowledge_state=KnowledgeState.KNOWN,
                value_shape=ValueShape.SCALAR,
                value="169",
                unit="hp",
                provenance_ref="raw:web:power",
            ).to_payload()

    def test_unknown_fact_cannot_smuggle_value_or_unit(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot carry"):
            PublishedEnrichmentFact(
                field="power",
                knowledge_state=KnowledgeState.UNKNOWN,
                value_shape=ValueShape.SCALAR,
                value=169,
                unit="hp",
                provenance_ref="raw:web:power",
            ).to_payload()

    def test_malformed_range_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "minValue cannot exceed maxValue"):
            PublishedEnrichmentFact(
                field="curb_weight",
                knowledge_state=KnowledgeState.KNOWN,
                value_shape=ValueShape.RANGE,
                value={"minValue": 1600, "maxValue": 1500},
                unit="kg",
                provenance_ref="raw:web:weight",
            ).to_payload()

    def test_unsupported_field_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported enrichment contract field"):
            PublishedEnrichmentFact(
                field="battery_magic_score",
                knowledge_state=KnowledgeState.UNKNOWN,
                provenance_ref="source:a",
            ).to_payload()

    def test_duplicate_public_fields_fail_closed(self) -> None:
        facts = [
            PublishedEnrichmentFact(
                field="power",
                knowledge_state=KnowledgeState.KNOWN,
                value_shape=ValueShape.SCALAR,
                value=value,
                unit="hp",
                provenance_ref=f"raw:web:power:{value}",
            )
            for value in (169, 170)
        ]

        with self.assertRaisesRegex(ValueError, "duplicate fields"):
            publish_enrichment_payload("podium7:vehicle:1", facts)


if __name__ == "__main__":
    unittest.main()
