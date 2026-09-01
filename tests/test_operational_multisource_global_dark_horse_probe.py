import json
from pathlib import Path
import tempfile
import unittest

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction
from podium7.operational_multisource import (
    build_multisource_operational_records,
    run_multisource_operational_records,
)
from podium7.operational_provenance import run_provenance_eligible_operational_corpus


GLOBAL_PATH = Path("benchmarks/catalog_identity_golden_v1.json")
BR_PATHS = (
    "benchmarks/catalog_identity_golden_br_v1.json",
    "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json",
)
ACTIVE_PATHS = (str(GLOBAL_PATH),) + BR_PATHS
RETAINED_ATTRIBUTION_PATH = "benchmarks/operational_multisource_field_attribution_v1.json"
SPEC_SOURCE = "ford-mustang-2024-eu-spec"
DARK_HORSE_GENERATION_SOURCE = "ford-mustang-dark-horse-2022"
GT_GENERATION_SOURCE = "ford-mustang-gt-performance-2024-br"
GT_GENERATION_URL = (
    "https://media.ford.com/content/fordmedia/fsa/br/pt/news/2024/03/"
    "ford-inicia-a-venda-do-mustang-gt-performance-de-setima-geracao-.html"
)
PROBE_KEYS = (
    ("1.0", "match-ford-mustang-dark-horse", "left"),
    ("1.0", "match-ford-mustang-dark-horse", "right"),
    ("1.0", "no-match-ford-mustang-gt-vs-dark-horse", "left"),
    ("1.0", "no-match-ford-mustang-gt-vs-dark-horse", "right"),
)


def _mapping(case_id: str, side: str, generation_source: str) -> dict:
    return {
        "benchmark": "catalog_identity_golden_v1.json",
        "benchmarkDatasetVersion": "1.0",
        "caseId": case_id,
        "side": side,
        "fieldSourceIds": {
            "make": [SPEC_SOURCE],
            "model": [SPEC_SOURCE],
            "generation": [generation_source],
            "variant": [SPEC_SOURCE],
            "powertrain": [SPEC_SOURCE],
            "body_style": [SPEC_SOURCE],
        },
        "evidenceBasis": {
            SPEC_SOURCE: (
                "Retained Ford technical specification establishes Mustang GT and Dark Horse "
                "trim labels, coupe body and 5.0 V8 configurations."
            ),
            DARK_HORSE_GENERATION_SOURCE: (
                "Retained Ford Dark Horse material explicitly places Dark Horse in the "
                "seventh-generation 2024 Mustang family."
            ),
            GT_GENERATION_SOURCE: (
                "Ford Brasil explicitly describes the Mustang GT Performance as seventh "
                "generation and a coupe with a Coyote V8 5.0."
            ),
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


PROBE_MAPPINGS = (
    _mapping("match-ford-mustang-dark-horse", "left", DARK_HORSE_GENERATION_SOURCE),
    _mapping("match-ford-mustang-dark-horse", "right", DARK_HORSE_GENERATION_SOURCE),
    _mapping("no-match-ford-mustang-gt-vs-dark-horse", "left", GT_GENERATION_SOURCE),
    _mapping("no-match-ford-mustang-gt-vs-dark-horse", "right", DARK_HORSE_GENERATION_SOURCE),
)


def _augmented_global_benchmark(path: Path) -> None:
    payload = json.loads(GLOBAL_PATH.read_text(encoding="utf-8"))
    payload["sources"].append(
        {
            "id": GT_GENERATION_SOURCE,
            "publisher": "Ford Motor Company",
            "title": "Ford inicia a venda do Mustang GT Performance de sétima geração no Brasil",
            "url": GT_GENERATION_URL,
            "supports": (
                "Ford Brasil explicitly identifies Mustang GT Performance as seventh generation, "
                "coupe and Coyote V8 5.0."
            ),
        }
    )
    target = [
        case
        for case in payload["cases"]
        if case["id"] == "no-match-ford-mustang-gt-vs-dark-horse"
    ]
    if len(target) != 1:
        raise AssertionError("Mustang GT vs Dark Horse case must resolve exactly once")
    target[0]["sourceIds"].append(GT_GENERATION_SOURCE)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _probe_records() -> list[dict]:
    overlay = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-global-mustang-1",
        "createdAt": "2026-09-01",
        "mappings": list(PROBE_MAPPINGS),
    }
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        global_path = root / GLOBAL_PATH.name
        overlay_path = root / "probe.json"
        _augmented_global_benchmark(global_path)
        overlay_path.write_text(json.dumps(overlay), encoding="utf-8")
        return build_multisource_operational_records(
            (global_path,) + tuple(Path(path) for path in BR_PATHS),
            overlay_path,
        )


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class GlobalMustangMultisourceProbeTests(unittest.TestCase):
    def test_probe_builds_all_four_composite_sides_with_explicit_generation_sources(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 4)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        self.assertEqual(
            set(records[2]["sourceIds"]),
            {SPEC_SOURCE, GT_GENERATION_SOURCE},
        )
        for index in (0, 1, 3):
            self.assertEqual(
                set(records[index]["sourceIds"]),
                {SPEC_SOURCE, DARK_HORSE_GENERATION_SOURCE},
            )

    def test_probe_replays_after_retained_corpus_with_field_level_provenance(self) -> None:
        store = CatalogStore()
        self.addCleanup(store.close)

        v1_report = run_provenance_eligible_operational_corpus(store, ACTIVE_PATHS)
        self.assertEqual(v1_report.total, 22)
        self.assertEqual(v1_report.failed, 0)

        retained_records = build_multisource_operational_records(
            ACTIVE_PATHS,
            RETAINED_ATTRIBUTION_PATH,
        )
        self.assertEqual(len(retained_records), 16)
        run_multisource_operational_records(store, retained_records)

        records = _probe_records()
        results = run_multisource_operational_records(store, records)
        allowed = {
            CatalogIngestionAction.CREATED,
            CatalogIngestionAction.MATCHED,
            CatalogIngestionAction.REVIEW,
        }
        self.assertEqual(len(results), 4)
        self.assertTrue(all(result.action in allowed for result in results))

        for record, result in zip(records, results):
            if result.action is CatalogIngestionAction.REVIEW:
                self.assertIsNotNone(result.review_id)
                continue
            self.assertIsNotNone(result.vehicle_id)
            expected_bindings = {
                (field_name, evidence_id)
                for field_name, evidence_ids in record["payload"]["provenance"]["fieldEvidence"].items()
                for evidence_id in evidence_ids
            }
            actual_bindings = {
                (fact.attribute, fact.evidence_id)
                for fact in store.catalog_candidates_for_entity(result.vehicle_id)
            }
            self.assertTrue(expected_bindings <= actual_bindings)


if __name__ == "__main__":
    unittest.main()
