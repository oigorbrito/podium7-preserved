from __future__ import annotations

import unittest

from podium7.catalog import CatalogMatchOutcome, CatalogVehicleIdentity
from podium7.catalog_resolution_precedence import (
    resolve_catalog_pair_with_structural_precedence,
)


class CatalogPartialLabelContradictionV1Tests(unittest.TestCase):
    def test_explicit_body_style_contradiction_outranks_partial_label_overlap(self) -> None:
        corolla_cross = CatalogVehicleIdentity(
            make="Toyota",
            model="Corolla Cross",
            generation="2020 global generation",
            powertrain="1.8 hybrid flex",
            body_style="SUV",
            market="BR",
        )
        corolla_sedan = CatalogVehicleIdentity(
            make="Toyota",
            model="Corolla",
            generation="12th generation",
            powertrain="hybrid",
            body_style="sedan",
        )

        decision = resolve_catalog_pair_with_structural_precedence(
            corolla_cross,
            corolla_sedan,
        )

        self.assertIs(decision.outcome, CatalogMatchOutcome.NO_MATCH)
        self.assertEqual(decision.reason, "generation differs")

    def test_partial_label_overlap_without_independent_contradiction_stays_review(self) -> None:
        specific = CatalogVehicleIdentity(
            make="Porsche",
            model="911 Carrera 4S",
            generation="992",
            powertrain="3.0 twin-turbo boxer six",
        )
        generic = CatalogVehicleIdentity(
            make="Porsche",
            model="911 Carrera",
            generation="992",
            powertrain="3.0 twin-turbo boxer six",
        )

        decision = resolve_catalog_pair_with_structural_precedence(specific, generic)

        self.assertIs(decision.outcome, CatalogMatchOutcome.REVIEW)
        self.assertEqual(decision.reason, "model labels partially overlap")

    def test_non_partial_decision_is_preserved(self) -> None:
        first = CatalogVehicleIdentity(make="Ford", model="Mustang", variant="GT")
        second = CatalogVehicleIdentity(make="Ford", model="Mustang", variant="Dark Horse")

        decision = resolve_catalog_pair_with_structural_precedence(first, second)

        self.assertIs(decision.outcome, CatalogMatchOutcome.NO_MATCH)
        self.assertEqual(decision.reason, "variant differs")


if __name__ == "__main__":
    unittest.main()
