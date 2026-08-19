import unittest

from podium7.domain import AutomotiveIdentity, EntityKind
from podium7.identity import MatchOutcome, generate_candidates, resolve_pair


def vehicle(**kwargs):
    defaults = dict(kind=EntityKind.POWERTRAIN, make="Chevrolet", model="Onix")
    defaults.update(kwargs)
    return AutomotiveIdentity(**defaults)


class EntityResolutionTests(unittest.TestCase):
    def test_same_vehicle_different_source_matches(self) -> None:
        a = vehicle(generation="II", powertrain="1.0 Turbo", year_from=2020, year_to=2024)
        b = vehicle(generation="II", powertrain="1.0 Turbo", year_from=2020, year_to=2024)
        self.assertEqual(resolve_pair(a, b).outcome, MatchOutcome.MATCH)

    def test_same_family_different_engine_no_match(self) -> None:
        a = vehicle(generation="II", powertrain="1.0", year_from=2020, year_to=2024)
        b = vehicle(generation="II", powertrain="1.0 Turbo", year_from=2020, year_to=2024)
        self.assertEqual(resolve_pair(a, b).outcome, MatchOutcome.NO_MATCH)

    def test_same_model_different_generation_no_match(self) -> None:
        a = vehicle(generation="I", powertrain="1.0", year_from=2013, year_to=2019)
        b = vehicle(generation="II", powertrain="1.0", year_from=2020, year_to=2024)
        self.assertEqual(resolve_pair(a, b).outcome, MatchOutcome.NO_MATCH)

    def test_alias_can_generate_candidate_and_match(self) -> None:
        target = vehicle(model="Onix Plus", aliases=("Onix Sedan",), generation="II", powertrain="1.0 Turbo")
        candidate = vehicle(model="Onix Sedan", aliases=("Onix Plus",), generation="II", powertrain="1.0 Turbo")
        generated = generate_candidates(target, [("candidate-1", candidate)])
        self.assertEqual([candidate_id for candidate_id, _ in generated], ["candidate-1"])
        self.assertEqual(resolve_pair(target, candidate).outcome, MatchOutcome.MATCH)

    def test_ambiguous_remains_unresolved(self) -> None:
        a = vehicle(generation="II")
        b = vehicle(generation="II")
        self.assertEqual(resolve_pair(a, b).outcome, MatchOutcome.UNRESOLVED)

    def test_blocking_excludes_other_make_or_model(self) -> None:
        target = vehicle()
        candidates = [
            ("same", vehicle()),
            ("other-model", vehicle(model="Tracker")),
            ("other-make", AutomotiveIdentity(kind=EntityKind.MODEL, make="Fiat", model="Onix")),
        ]
        generated = generate_candidates(target, candidates)
        self.assertEqual([candidate_id for candidate_id, _ in generated], ["same"])


if __name__ == "__main__":
    unittest.main()
