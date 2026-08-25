import unittest

from podium7.domain import CandidateFact
from podium7.multisource_validation import MultiSourceCase, SourceCandidate, evaluate_multisource_cases


def fact(source, case, attribute, value, unit=None):
    return SourceCandidate(
        source_id=source,
        fact=CandidateFact(
            id=f"{source}:{case}:{attribute}:{value}",
            entity_candidate_id=f"candidate:{case}",
            attribute=attribute,
            raw_value=value,
            normalized_value=value,
            unit=unit,
            evidence_id=f"evidence:{source}:{case}",
            extraction_method=f"fixture:{source}",
        ),
    )


class MultiSourceValidationTests(unittest.TestCase):
    def corpus(self):
        return (
            MultiSourceCase(
                "corroborated-make",
                "vehicle:corroborated",
                "make",
                (fact("nhtsa_vpic", "corroborated", "make", "VOLVO"), fact("eea_co2_cars", "corroborated", "make", "VOLVO")),
                "CANONICAL",
                "two qualified source families agree on the normalized make",
            ),
            MultiSourceCase(
                "single-source-regulatory-variant",
                "vehicle:eea-only",
                "eea.variant",
                (fact("eea_co2_cars", "eea-only", "eea.variant", "UZH4"),),
                "CANONICAL",
                "EEA regulatory variant remains a source-scoped fact rather than retail trim",
            ),
            MultiSourceCase(
                "conflicting-power",
                "vehicle:power-conflict",
                "power",
                (fact("eea_co2_cars", "power-conflict", "power", 186, "kW"), fact("nhtsa_vpic", "power-conflict", "power", 190, "kW")),
                "CONFLICT",
                "normalized disagreement must remain an explicit conflict",
            ),
            MultiSourceCase(
                "registration-year-not-model-year",
                "vehicle:year-boundary",
                "eea.registration_year",
                (fact("eea_co2_cars", "year-boundary", "eea.registration_year", 2025),),
                "CANONICAL",
                "registration year is retained only in its source semantic namespace",
            ),
            MultiSourceCase(
                "unsupported-retail-trim",
                "vehicle:trim-gap",
                "variant",
                (),
                "REVIEW",
                "regulatory source fields do not justify a retail variant guess",
            ),
            MultiSourceCase(
                "unsupported-manufacture-year",
                "vehicle:manufacture-year-gap",
                "manufacture_year",
                (),
                "REVIEW",
                "model or registration year must not be substituted for manufacture year",
            ),
        )

    def test_bounded_corpus_measures_corroboration_conflict_review_and_provenance(self):
        report = evaluate_multisource_cases(self.corpus())
        summary = report["summary"]
        self.assertEqual(6, summary["cases"])
        self.assertEqual(3, summary["canonicalCases"])
        self.assertEqual(1, summary["corroboratedCases"])
        self.assertEqual(1, summary["conflictCases"])
        self.assertEqual(2, summary["reviewCases"])
        self.assertEqual(0, summary["incorrectCases"])
        self.assertEqual(6, summary["provenanceCompleteCases"])
        self.assertEqual(1.0, summary["provenanceCompleteness"])
        self.assertEqual(0, summary["resolverPolicyChanges"])
        self.assertEqual({"eea_co2_cars": 4, "nhtsa_vpic": 2}, summary["sourceContribution"])

    def test_conflict_is_not_silently_collapsed(self):
        report = evaluate_multisource_cases(self.corpus())
        conflict = next(item for item in report["results"] if item["caseId"] == "conflicting-power")
        self.assertEqual("CONFLICT", conflict["disposition"])
        self.assertEqual(2, len(conflict["candidateReferences"]))

    def test_unsupported_dimensions_remain_review(self):
        report = evaluate_multisource_cases(self.corpus())
        review_ids = {item["caseId"] for item in report["results"] if item["disposition"] == "REVIEW"}
        self.assertEqual({"unsupported-retail-trim", "unsupported-manufacture-year"}, review_ids)


if __name__ == "__main__":
    unittest.main()
