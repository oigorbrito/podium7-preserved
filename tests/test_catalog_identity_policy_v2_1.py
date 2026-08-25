import unittest

from podium7.catalog import (
    CatalogMatchOutcome,
    CatalogVehicleIdentity,
    ExternalIdentifier,
    ExternalIdentifierStrength,
    resolve_catalog_pair,
)
from podium7.catalog_resolution_precedence import (
    resolve_catalog_pair_with_structural_precedence,
)


def vehicle(**kwargs):
    defaults = dict(make="Toyota", model="Corolla")
    defaults.update(kwargs)
    return CatalogVehicleIdentity(**defaults)


class CatalogExternalIdentifierPolicyTests(unittest.TestCase):
    def test_unknown_namespace_shared_identifier_does_not_auto_match(self) -> None:
        identifier = ExternalIdentifier("unknown-source", "shared-123")
        decision = resolve_catalog_pair(
            vehicle(external_identifiers=(identifier,)),
            vehicle(external_identifiers=(identifier,)),
        )
        self.assertEqual(decision.outcome, CatalogMatchOutcome.REVIEW)

    def test_supporting_namespace_shared_identifier_does_not_auto_match_alone(self) -> None:
        identifier = ExternalIdentifier("fipe", "004001-0")
        decision = resolve_catalog_pair(
            vehicle(external_identifiers=(identifier,)),
            vehicle(external_identifiers=(identifier,)),
        )
        self.assertEqual(decision.outcome, CatalogMatchOutcome.REVIEW)

    def test_strong_namespace_shared_identifier_matches_without_contradiction(self) -> None:
        identifier = ExternalIdentifier("test-strong", "shared-123")
        registry = {"test-strong": ExternalIdentifierStrength.STRONG}
        decision = resolve_catalog_pair(
            vehicle(external_identifiers=(identifier,)),
            vehicle(external_identifiers=(identifier,)),
            namespace_registry=registry,
        )
        self.assertEqual(decision.outcome, CatalogMatchOutcome.MATCH)

    def test_strong_identifier_does_not_override_explicit_contradiction(self) -> None:
        identifier = ExternalIdentifier("test-strong", "shared-123")
        registry = {"test-strong": ExternalIdentifierStrength.STRONG}
        decision = resolve_catalog_pair(
            vehicle(generation="E170", external_identifiers=(identifier,)),
            vehicle(generation="E210", external_identifiers=(identifier,)),
            namespace_registry=registry,
        )
        self.assertEqual(decision.outcome, CatalogMatchOutcome.NO_MATCH)

    def test_operational_precedence_preserves_external_identifier_policy(self) -> None:
        unknown = ExternalIdentifier("unknown-source", "shared-123")
        fipe = ExternalIdentifier("fipe", "004001-0")
        strong = ExternalIdentifier("test-strong", "shared-123")
        registry = {"test-strong": ExternalIdentifierStrength.STRONG}
        cases = (
            (
                vehicle(external_identifiers=(unknown,)),
                vehicle(external_identifiers=(unknown,)),
                None,
                CatalogMatchOutcome.REVIEW,
            ),
            (
                vehicle(external_identifiers=(fipe,)),
                vehicle(external_identifiers=(fipe,)),
                None,
                CatalogMatchOutcome.REVIEW,
            ),
            (
                vehicle(external_identifiers=(strong,)),
                vehicle(external_identifiers=(strong,)),
                registry,
                CatalogMatchOutcome.MATCH,
            ),
            (
                vehicle(generation="E170", external_identifiers=(strong,)),
                vehicle(generation="E210", external_identifiers=(strong,)),
                registry,
                CatalogMatchOutcome.NO_MATCH,
            ),
        )

        for left, right, namespace_registry, expected in cases:
            with self.subTest(expected=expected.value):
                canonical = resolve_catalog_pair(
                    left,
                    right,
                    namespace_registry=namespace_registry,
                )
                operational = resolve_catalog_pair_with_structural_precedence(
                    left,
                    right,
                    namespace_registry=namespace_registry,
                )
                self.assertEqual(operational, canonical)
                self.assertIs(operational.outcome, expected)


if __name__ == "__main__":
    unittest.main()
