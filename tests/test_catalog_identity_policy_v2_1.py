import unittest

from podium7.catalog import (
    CatalogMatchOutcome,
    CatalogVehicleIdentity,
    ExternalIdentifier,
    ExternalIdentifierStrength,
    resolve_catalog_pair,
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


if __name__ == "__main__":
    unittest.main()
