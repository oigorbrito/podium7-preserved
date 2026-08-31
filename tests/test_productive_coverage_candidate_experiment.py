import copy
import json
from pathlib import Path
import tempfile
import unittest

from podium7.operational_provenance import measure_operational_provenance_eligibility


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_DATASET = ROOT / "benchmarks" / "catalog_identity_golden_v1.json"
BR_DATASET = ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json"
BR_ADJACENT_DATASET = ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json"
ACTIVE_DATASETS = (GLOBAL_DATASET, BR_DATASET, BR_ADJACENT_DATASET)

CANDIDATE_ATTRIBUTIONS = {
    "catalog_identity_golden_v1.json": {
        "no-match-toyota-corolla-10g-vs-12g": {
            "left": "toyota-corolla-2006-global",
            "right": "toyota-corolla-2018-global",
        },
    },
    "catalog_identity_golden_br_v1.json": {
        "br-no-match-corsa-shared-fipe-different-model-year": {
            "left": "corsa-wind-fipe-code-secondary",
            "right": "corsa-wind-fipe-code-secondary",
        },
        "br-review-shared-fipe-code-alone": {
            "left": "corsa-wind-fipe-code-secondary",
            "right": "corsa-wind-fipe-code-secondary",
        },
    },
    "catalog_identity_br_adjacent_incomplete_v1.json": {
        "br-hard-no-match-corolla-altis-hybrid-my25-vs-my26": {
            "left": "toyota-connected-services-corolla-my25",
            "right": "toyota-corolla-altis-hybrid-offer-2026",
        },
        "br-hard-no-match-onix-premier-my26-vs-my27": {
            "left": "chevrolet-onix-my26-price-list",
            "right": "chevrolet-onix-line-2027",
        },
    },
}


def _write_payload(payload: dict) -> Path:
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False)
    with handle:
        json.dump(payload, handle)
    return Path(handle.name)


def _attribute_all_present_fields(side: dict, source_id: str) -> dict[str, list[str]]:
    return {
        field_name: [source_id]
        for field_name, value in side.items()
        if value is not None and not (isinstance(value, (list, tuple)) and not value)
    }


def _experiment_dataset(path: Path, attributions: dict[str, dict[str, str]]) -> Path:
    payload = json.loads(path.read_text(encoding="utf-8"))
    experiment = copy.deepcopy(payload)
    cases = {case["id"]: case for case in experiment["cases"]}
    for case_id, side_sources in attributions.items():
        target = cases[case_id]
        target["fieldSourceIds"] = {
            side: _attribute_all_present_fields(target[side], source_id)
            for side, source_id in side_sources.items()
        }
    return _write_payload(experiment)


class ProductiveCoverageCandidateExperimentTests(unittest.TestCase):
    def test_corolla_generation_pair_is_replayable_with_explicit_side_sources_only(self) -> None:
        path = _experiment_dataset(
            GLOBAL_DATASET,
            CANDIDATE_ATTRIBUTIONS[GLOBAL_DATASET.name],
        )
        self.addCleanup(path.unlink, missing_ok=True)

        report = measure_operational_provenance_eligibility(
            (path, BR_DATASET, BR_ADJACENT_DATASET)
        )
        summary = report["summary"]

        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 14)
        self.assertEqual(summary["blockedRecords"], 46)
        self.assertEqual(
            summary["replayableByMethod"],
            {"EXPLICIT_FIELD_ATTRIBUTION": 2, "SOLE_CASE_SOURCE": 12},
        )

        target_records = [
            record
            for record in report["records"]
            if record["caseId"] == "no-match-toyota-corolla-10g-vs-12g"
        ]
        self.assertEqual(len(target_records), 2)
        self.assertTrue(all(record["replayable"] for record in target_records))
        self.assertEqual(
            [record["sourceId"] for record in target_records],
            ["toyota-corolla-2006-global", "toyota-corolla-2018-global"],
        )
        self.assertTrue(
            all(
                record["method"] == "EXPLICIT_FIELD_ATTRIBUTION"
                for record in target_records
            )
        )

    def test_all_ten_classified_candidates_reach_frozen_contract_upper_bound(self) -> None:
        experiment_paths: list[Path] = []
        for retained in ACTIVE_DATASETS:
            attributions = CANDIDATE_ATTRIBUTIONS.get(retained.name, {})
            experiment = _experiment_dataset(retained, attributions)
            experiment_paths.append(experiment)
            self.addCleanup(experiment.unlink, missing_ok=True)

        report = measure_operational_provenance_eligibility(experiment_paths)
        summary = report["summary"]

        self.assertEqual(summary["records"], 60)
        self.assertEqual(summary["replayableRecords"], 22)
        self.assertEqual(summary["blockedRecords"], 38)
        self.assertEqual(summary["replayableRate"], 22 / 60)
        self.assertEqual(
            summary["replayableByMethod"],
            {"EXPLICIT_FIELD_ATTRIBUTION": 10, "SOLE_CASE_SOURCE": 12},
        )

        candidate_records = [
            record
            for record in report["records"]
            if record["method"] == "EXPLICIT_FIELD_ATTRIBUTION"
        ]
        self.assertEqual(len(candidate_records), 10)
        self.assertTrue(all(record["replayable"] for record in candidate_records))

        expected = {
            (case_id, side, source_id)
            for dataset_cases in CANDIDATE_ATTRIBUTIONS.values()
            for case_id, sides in dataset_cases.items()
            for side, source_id in sides.items()
        }
        observed = {
            (record["caseId"], record["side"], record["sourceId"])
            for record in candidate_records
        }
        self.assertEqual(observed, expected)

    def test_experiment_does_not_mutate_any_retained_dataset(self) -> None:
        before = {path: path.read_bytes() for path in ACTIVE_DATASETS}
        experiment_paths: list[Path] = []
        for retained in ACTIVE_DATASETS:
            attributions = CANDIDATE_ATTRIBUTIONS.get(retained.name, {})
            experiment = _experiment_dataset(retained, attributions)
            experiment_paths.append(experiment)
            self.addCleanup(experiment.unlink, missing_ok=True)

        measure_operational_provenance_eligibility(experiment_paths)

        self.assertEqual(
            before,
            {path: path.read_bytes() for path in ACTIVE_DATASETS},
        )


if __name__ == "__main__":
    unittest.main()
