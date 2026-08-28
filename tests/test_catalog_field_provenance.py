import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog_benchmark import load_catalog_identity_benchmark
from podium7.catalog_quality import measure_field_source_contribution


ROOT = Path(__file__).resolve().parents[1]
V3_DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
    ROOT / "benchmarks" / "catalog_identity_year_semantics_challenge_v1.json",
)


def _payload() -> dict:
    return {
        "schema": "podium7.catalog-identity-golden.v1",
        "datasetVersion": "field-provenance-test-1",
        "sources": [
            {"id": "source-a", "url": "https://example.com/a"},
            {"id": "source-b", "url": "https://example.com/b"},
        ],
        "cases": [
            {
                "id": "explicit-attribution",
                "expected": "MATCH",
                "left": {
                    "make": "Example",
                    "model": "Road",
                    "model_year_from": 2026,
                    "model_year_to": 2026,
                },
                "right": {
                    "make": "Example",
                    "model": "Road",
                    "model_year_from": 2026,
                    "model_year_to": 2026,
                },
                "sourceIds": ["source-a", "source-b"],
                "fieldSourceIds": {
                    "left": {
                        "make": ["source-a"],
                        "model": ["source-a", "source-b"],
                        "model_year_from": ["source-b"],
                    },
                    "right": {
                        "make": ["source-a"],
                        "model": ["source-b"],
                    },
                },
                "rationale": "Synthetic contract fixture for explicit attribution validation only.",
            }
        ],
    }


def _write_payload(payload: object) -> Path:
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
    with handle:
        json.dump(payload, handle)
    return Path(handle.name)


class CatalogFieldProvenanceTests(unittest.TestCase):
    def test_explicit_field_sources_are_loaded_and_measured_without_inference(self) -> None:
        path = _write_payload(_payload())
        self.addCleanup(path.unlink, missing_ok=True)

        dataset = load_catalog_identity_benchmark(path)
        case = dataset.cases[0]
        self.assertEqual(case.left_field_source_ids["model"], ("source-a", "source-b"))
        self.assertEqual(case.right_field_source_ids["make"], ("source-a",))

        report = measure_field_source_contribution((path,))
        self.assertEqual(report["totalPresentFieldObservations"], 8)
        self.assertEqual(report["attributedFieldObservations"], 5)
        self.assertEqual(report["attributionCoverage"], 5 / 8)
        self.assertEqual(report["totalByDimension"], {
            "make": 2,
            "model": 2,
            "model_year_from": 2,
            "model_year_to": 2,
        })
        self.assertEqual(report["attributedByDimension"], {
            "make": 2,
            "model": 2,
            "model_year_from": 1,
        })
        self.assertEqual(report["unattributedByDimension"], {
            "make": 0,
            "model": 0,
            "model_year_from": 1,
            "model_year_to": 2,
        })
        self.assertEqual(report["sourceContributionByDimension"], {
            "make": {"source-a": 2},
            "model": {"source-a": 1, "source-b": 2},
            "model_year_from": {"source-b": 1},
        })

    def test_legacy_case_remains_valid_but_is_explicitly_unattributed(self) -> None:
        payload = _payload()
        del payload["cases"][0]["fieldSourceIds"]
        path = _write_payload(payload)
        self.addCleanup(path.unlink, missing_ok=True)

        dataset = load_catalog_identity_benchmark(path)
        self.assertEqual(dataset.cases[0].left_field_source_ids, {})
        self.assertEqual(dataset.cases[0].right_field_source_ids, {})

        report = measure_field_source_contribution((path,))
        self.assertEqual(report["attributedFieldObservations"], 0)
        self.assertEqual(report["attributionCoverage"], 0.0)
        self.assertEqual(report["sourceContributionByDimension"], {})
        self.assertTrue(all(value > 0 for value in report["unattributedByDimension"].values()))

    def test_existing_v3_corpus_reports_missing_field_attribution_instead_of_inferring_it(self) -> None:
        report = measure_field_source_contribution(V3_DATASETS)
        self.assertGreater(report["totalPresentFieldObservations"], 0)
        self.assertEqual(report["attributedFieldObservations"], 0)
        self.assertEqual(report["attributionCoverage"], 0.0)
        self.assertEqual(report["sourceContributionByDimension"], {})
        self.assertEqual(
            sum(report["unattributedByDimension"].values()),
            report["totalPresentFieldObservations"],
        )

    def test_field_attribution_rejects_unknown_source(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["make"] = ["not-declared"]
        self._assert_invalid(payload, "outside case sourceIds")

    def test_field_attribution_rejects_unknown_field(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["paint_code"] = ["source-a"]
        self._assert_invalid(payload, "unknown identity field")

    def test_field_attribution_rejects_absent_field(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["transmission"] = ["source-a"]
        self._assert_invalid(payload, "attributes an absent field")

    def test_field_attribution_rejects_empty_source_list(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["make"] = []
        self._assert_invalid(payload, "requires a non-empty source list")

    def test_field_attribution_rejects_duplicate_source_ids(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["left"]["make"] = ["source-a", "source-a"]
        self._assert_invalid(payload, "source ids must be unique")

    def test_field_attribution_rejects_unknown_side(self) -> None:
        payload = _payload()
        payload["cases"][0]["fieldSourceIds"]["canonical"] = {"make": ["source-a"]}
        self._assert_invalid(payload, "unknown side")

    def test_malformed_source_and_case_containers_fail_closed(self) -> None:
        payload = _payload()
        payload["sources"][0] = "not-an-object"
        self._assert_invalid(payload, "sources must be a non-empty array of objects")

        payload = _payload()
        payload["cases"][0] = "not-an-object"
        self._assert_invalid(payload, "cases must be a non-empty array of objects")

    def test_source_ids_and_identity_containers_fail_closed(self) -> None:
        payload = _payload()
        payload["cases"][0]["sourceIds"] = "source-a"
        self._assert_invalid(payload, "sourceIds must be a non-empty array")

        payload = _payload()
        payload["cases"][0]["left"] = "not-an-object"
        self._assert_invalid(payload, "left and right identities must be objects")

    def test_identity_list_defaults_can_be_omitted(self) -> None:
        payload = _payload()
        # Remove list fields which should default to empty lists
        payload["cases"][0]["left"].pop("aliases", None)
        payload["cases"][0]["left"].pop("engine_identifiers", None)
        payload["cases"][0]["left"].pop("external_identifiers", None)
        # Should parse successfully without ValueError
        path = _write_payload(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        load_catalog_identity_benchmark(path)

    def _assert_invalid(self, payload: object, message: str) -> None:
        path = _write_payload(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        with self.assertRaisesRegex(ValueError, message):
            load_catalog_identity_benchmark(path)


if __name__ == "__main__":
    unittest.main()
