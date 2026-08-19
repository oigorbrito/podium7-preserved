import unittest

from podium7.domain import AutomotiveIdentity, EntityKind


class AutomotiveIdentityInvariantTests(unittest.TestCase):
    def test_identity_requires_entity_kind_and_non_empty_optional_tokens(self):
        with self.assertRaises(ValueError):
            AutomotiveIdentity(kind="Model", make="Example")

        base = {
            "kind": EntityKind.POWERTRAIN,
            "make": "Example",
            "model": "Model",
            "generation": "Generation",
            "variant": "Variant",
            "powertrain": "Powertrain",
            "market": "BR",
        }
        for field in ("model", "generation", "variant", "powertrain", "market"):
            invalid = dict(base)
            invalid[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    AutomotiveIdentity(**invalid)

    def test_identity_years_must_be_integers_when_provided(self):
        for field, value in (
            ("year_from", 2020.5),
            ("year_to", 2024.5),
            ("year_from", True),
            ("year_to", False),
        ):
            kwargs = {"kind": EntityKind.MODEL, "make": "Example", field: value}
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    AutomotiveIdentity(**kwargs)

    def test_identity_evidence_tokens_must_be_non_empty_and_unique(self):
        cases = (
            {"aliases": ("Alias", "Alias")},
            {"aliases": ("",)},
            {"engine_identifiers": ("ENG-1", "ENG-1")},
            {"engine_identifiers": ("",)},
            {"external_identifiers": ("ext-1", "ext-1")},
            {"external_identifiers": ("",)},
        )
        for extra in cases:
            with self.subTest(extra=extra):
                with self.assertRaises(ValueError):
                    AutomotiveIdentity(kind=EntityKind.MODEL, make="Example", **extra)


if __name__ == "__main__":
    unittest.main()
