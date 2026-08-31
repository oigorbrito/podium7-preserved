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


class ProductiveCoverageCandidateExperimentTests(unittest.TestCase):
    def test_corolla_generation_pair_is_replayable_with_explicit_side_sources_only(self) -> None:
        payload = json.loads(GLOBAL_DATASET.read_text(encoding="utf-8"))
        experiment = copy.deepcopy(payload)
        target = next(
            case
            for case in experiment["cases"]
            if case["id"] == "no-match-toyota-corolla-10g-vs-12g"
        )

        target["fieldSourceIds"] = {
            "left": _attribute_all_present_fields(
                target["left"], "toyota-corolla-2006-global"
            ),
            "right": _attribute_all_present_fields(
                target["right"], "toyota-corolla-2018-global"
            ),
        }

        path = _write_payload(experiment)
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

    def test_experiment_does_not_mutate_retained_dataset(self) -> None:
        before = GLOBAL_DATASET.read_bytes()
        payload = json.loads(before)
        target = next(
            case
            for case in payload["cases"]
            if case["id"] == "no-match-toyota-corolla-10g-vs-12g"
        )
        target["fieldSourceIds"] = {
            "left": _attribute_all_present_fields(
                target["left"], "toyota-corolla-2006-global"
            ),
            "right": _attribute_all_present_fields(
                target["right"], "toyota-corolla-2018-global"
            ),
        }
        path = _write_payload(payload)
        self.addCleanup(path.unlink, missing_ok=True)
        measure_operational_provenance_eligibility((path,))

        self.assertEqual(before, GLOBAL_DATASET.read_bytes())


if __name__ == "__main__":
    unittest.main()
