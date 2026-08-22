import unittest

from podium7.catalog import (
    CatalogChangeImpact,
    CatalogPublicationAction,
    CatalogVehicleIdentity,
    ExternalIdentifier,
    catalog_change_impact,
    validate_catalog_publication_change,
)
from podium7.domain import DecisionStatus


def vehicle(**kwargs):
    defaults = dict(make="Toyota", model="Corolla", generation="E210")
    defaults.update(kwargs)
    return CatalogVehicleIdentity(**defaults)


class CatalogEvidencePolicyTests(unittest.TestCase):
    def test_external_creation_requires_evidence_backed_reference(self) -> None:
        identity = vehicle()
        with self.assertRaises(ValueError):
            validate_catalog_publication_change(
                None,
                identity,
                action=CatalogPublicationAction.CREATE,
                decision_status=DecisionStatus.EVIDENCE_BACKED,
            )
        with self.assertRaises(ValueError):
            validate_catalog_publication_change(
                None,
                identity,
                action=CatalogPublicationAction.CREATE,
                decision_status=DecisionStatus.HYPOTHESIS,
                evidence_ids=("ev-1",),
            )
        impact = validate_catalog_publication_change(
            None,
            identity,
            action=CatalogPublicationAction.CREATE,
            decision_status=DecisionStatus.EVIDENCE_BACKED,
            evidence_ids=("ev-1",),
        )
        self.assertEqual(impact, CatalogChangeImpact.IDENTITY)

    def test_correction_requires_evidence_and_reason(self) -> None:
        before = vehicle(generation="E170")
        after = vehicle(generation="E210")
        with self.assertRaises(ValueError):
            validate_catalog_publication_change(
                before,
                after,
                action=CatalogPublicationAction.CORRECTION,
                decision_status=DecisionStatus.EVIDENCE_BACKED,
                evidence_ids=("ev-2",),
            )
        impact = validate_catalog_publication_change(
            before,
            after,
            action=CatalogPublicationAction.CORRECTION,
            decision_status=DecisionStatus.EVIDENCE_BACKED,
            evidence_ids=("ev-2",),
            reason="correct generation",
        )
        self.assertEqual(impact, CatalogChangeImpact.IDENTITY)

    def test_administrative_override_is_explicit_engineering_choice(self) -> None:
        before = vehicle(generation="E170")
        after = vehicle(generation="E210")
        invalid_cases = (
            dict(decision_status=DecisionStatus.EVIDENCE_BACKED, actor_id="admin", reason="override"),
            dict(decision_status=DecisionStatus.ENGINEERING_CHOICE, actor_id=None, reason="override"),
            dict(decision_status=DecisionStatus.ENGINEERING_CHOICE, actor_id="admin", reason=None),
        )
        for kwargs in invalid_cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    validate_catalog_publication_change(
                        before,
                        after,
                        action=CatalogPublicationAction.ADMINISTRATIVE_OVERRIDE,
                        **kwargs,
                    )
        impact = validate_catalog_publication_change(
            before,
            after,
            action=CatalogPublicationAction.ADMINISTRATIVE_OVERRIDE,
            decision_status=DecisionStatus.ENGINEERING_CHOICE,
            actor_id="admin",
            reason="manual catalog correction",
        )
        self.assertEqual(impact, CatalogChangeImpact.IDENTITY)

    def test_change_impact_separates_semantic_identity_from_informational_edits(self) -> None:
        base = vehicle()
        case_only = vehicle(make="TOYOTA")
        reference_only = vehicle(
            external_identifiers=(ExternalIdentifier("unknown-source", "ref-1"),)
        )
        supporting = vehicle(
            external_identifiers=(ExternalIdentifier("fipe", "004001-0"),)
        )
        alias_change = vehicle(aliases=("Corolla Altis",))

        self.assertEqual(catalog_change_impact(base, case_only), CatalogChangeImpact.INFORMATIONAL)
        self.assertEqual(catalog_change_impact(base, reference_only), CatalogChangeImpact.INFORMATIONAL)
        self.assertEqual(catalog_change_impact(base, supporting), CatalogChangeImpact.IDENTITY)
        self.assertEqual(catalog_change_impact(base, alias_change), CatalogChangeImpact.IDENTITY)


if __name__ == "__main__":
    unittest.main()
