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
        self.assertEqual({"UNRESOLVED": 1}, summary["conflictsByState"])
        self.assertEqual(2, summary["reviewCases"])
        self.assertEqual(0, summary["incorrectCases"])
        self.assertEqual(4, summary["provenanceApplicableCases"])
        self.assertEqual(4, summary["provenanceCompleteCases"])
        self.assertEqual(1.0, summary["provenanceCompleteness"])
        self.assertEqual(0, summary["resolverPolicyChanges"])
        self.assertEqual({"eea_co2_cars": 4, "nhtsa_vpic": 2}, summary["sourceContribution"])

    def test_conflict_is_not_silently_collapsed_and_references_all_inputs(self):
        report = evaluate_multisource_cases(self.corpus())
        conflict = next(item for item in report["results"] if item["caseId"] == "conflicting-power")
        self.assertEqual("CONFLICT", conflict["disposition"])
        self.assertEqual("UNRESOLVED", conflict["conflictState"])
        self.assertEqual(2, len(conflict["candidateReferences"]))
        self.assertTrue(conflict["provenanceComplete"])

    def test_unsupported_dimensions_remain_review_and_provenance_is_not_applicable(self):
        report = evaluate_multisource_cases(self.corpus())
        reviews = [item for item in report["results"] if item["disposition"] == "REVIEW"]
        self.assertEqual(
            {"unsupported-retail-trim", "unsupported-manufacture-year"},
            {item["caseId"] for item in reviews},
        )
        self.assertTrue(all(item["conflictState"] is None for item in reviews))
        self.assertTrue(all(item["provenanceComplete"] is None for item in reviews))
        self.assertEqual({"UNRESOLVED": 1}, report["summary"]["conflictsByState"])

    def test_non_conflict_results_have_no_conflict_state(self):
        report = evaluate_multisource_cases(self.corpus())
        self.assertTrue(
            all(
                item["conflictState"] is None
                for item in report["results"]
                if item["disposition"] != "CONFLICT"
            )
        )

    def test_duplicate_case_ids_are_rejected_before_measurement(self):
        case = self.corpus()[0]
        with self.assertRaisesRegex(ValueError, "case ids must be unique"):
            evaluate_multisource_cases((case, case))

    def test_duplicate_candidate_fact_ids_fail_closed(self):
        candidate = fact("nhtsa_vpic", "duplicate", "make", "VOLVO")
        with self.assertRaisesRegex(ValueError, "candidate fact ids must be unique"):
            MultiSourceCase(
                "duplicate-fact",
                "vehicle:duplicate",
                "make",
                (candidate, SourceCandidate("eea_co2_cars", candidate.fact)),
                "CANONICAL",
                "same fact cannot count as two source candidates",
            )

    def test_candidate_container_must_be_tuple(self):
        with self.assertRaisesRegex(ValueError, "candidates must be a tuple"):
            MultiSourceCase(
                "wrong-container",
                "vehicle:test",
                "make",
                [],  # type: ignore[arg-type]
                "REVIEW",
                "malformed fixture",
            )

    def test_required_text_and_source_id_cannot_be_whitespace(self):
        with self.assertRaisesRegex(ValueError, "source_id is required"):
            fact("   ", "blank-source", "make", "VOLVO")
        with self.assertRaisesRegex(ValueError, "case_id is required"):
            MultiSourceCase(
                "   ",
                "vehicle:test",
                "make",
                (),
                "REVIEW",
                "missing evidence",
            )
        with self.assertRaisesRegex(ValueError, "rationale is required"):
            MultiSourceCase(
                "blank-rationale",
                "vehicle:test",
                "make",
                (),
                "REVIEW",
                "   ",
            )


if __name__ == "__main__":
    unittest.main()
