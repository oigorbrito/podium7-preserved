from pathlib import Path
import unittest

from podium7.operational_provenance import build_provenance_eligible_operational_records
from podium7.source_backed_enrichment import (
    apply_source_backed_overrides_to_records,
    evaluate_source_backed_enrichment,
    load_source_backed_enrichment_overrides,
)


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
ENRICHMENT = ROOT / "benchmarks" / "source_backed_enrichment_v1.json"


class SourceBackedEnrichmentApplicationV1Tests(unittest.TestCase):
    def test_explicit_source_field_resolves_one_review_while_ambiguity_stays_review(self) -> None:
        report = evaluate_source_backed_enrichment(DATASETS, ENRICHMENT)

        self.assertEqual(report["summary"], {
            "observations": 3,
            "resolvedReviews": 1,
            "retainedReviews": 2,
            "incorrect": 0,
            "resolverPolicyChanges": 0,
        })
        by_id = {item["id"]: item for item in report["results"]}
        self.assertEqual(by_id["toyota-corolla-sedan-body-style-reextraction"]["after"], "MATCH")
        self.assertEqual(by_id["ford-mustang-missing-variant-remains-ambiguous"]["after"], "REVIEW")
        self.assertEqual(by_id["porsche-carrera-partial-label-remains-ambiguous"]["after"], "REVIEW")
        self.assertTrue(all(item["resolverPolicyChange"] is False for item in report["results"]))

    def test_operational_override_is_narrow_and_does_not_overwrite_existing_identity(self) -> None:
        overrides = load_source_backed_enrichment_overrides(DATASETS, ENRICHMENT)
        self.assertEqual(overrides, {
            "operational:1.0:review-toyota-corolla-body-style-missing:right": {
                "body_style": "sedan",
            }
        })

        records = build_provenance_eligible_operational_records(DATASETS)
        enriched = apply_source_backed_overrides_to_records(records, overrides)
        target = next(
            item
            for item in enriched
            if item["evidence"]["id"] == "operational:1.0:review-toyota-corolla-body-style-missing:right"
        )
        self.assertEqual(target["vehicle"]["body_style"], "sedan")
        self.assertEqual(len(enriched), len(records))

        conflicting = [dict(item) for item in records]
        target_index = next(
            index
            for index, item in enumerate(conflicting)
            if item["evidence"]["id"] == "operational:1.0:review-toyota-corolla-body-style-missing:right"
        )
        conflicting[target_index] = {
            **conflicting[target_index],
            "vehicle": {**conflicting[target_index]["vehicle"], "body_style": "wagon"},
        }
        with self.assertRaisesRegex(ValueError, "cannot overwrite"):
            apply_source_backed_overrides_to_records(conflicting, overrides)


if __name__ == "__main__":
    unittest.main()
