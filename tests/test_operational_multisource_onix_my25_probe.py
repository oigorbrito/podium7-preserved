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


GLOBAL_PATH = "benchmarks/catalog_identity_golden_v1.json"
BR_PATH = Path("benchmarks/catalog_identity_golden_br_v1.json")
ADJACENT_PATH = "benchmarks/catalog_identity_br_adjacent_incomplete_v1.json"
ACTIVE_PATHS = (GLOBAL_PATH, str(BR_PATH), ADJACENT_PATH)
RETAINED_ATTRIBUTION_PATH = "benchmarks/operational_multisource_field_attribution_v1.json"
GENERATION_SOURCE = "chevrolet-onix-second-generation"
PRICE_SOURCE = "chevrolet-onix-my25-price-list"
OWNER_MANUAL_SOURCE = "chevrolet-onix-2025-owner-manual"
OWNER_MANUAL_URL = (
    "https://www.chevrolet.com.br/content/dam/chevrolet/south-america/brazil/portuguese/"
    "index/visid/services/manuals/pdfs/onix/01-pdfs/2025/onix-2025-manual-do-propietario.pdf"
)
PROBE_KEYS = (
    ("br-1.0", "br-match-onix-premier-turbo-my25", "left"),
    ("br-1.0", "br-match-onix-premier-turbo-my25", "right"),
    ("br-1.0", "br-review-onix-premier-missing-variant", "left"),
    ("br-1.0", "br-review-onix-premier-missing-variant", "right"),
)


def _mapping(case_id: str, side: str, *, include_variant: bool) -> dict:
    field_sources = {
        "make": [PRICE_SOURCE],
        "model": [PRICE_SOURCE],
        "generation": [GENERATION_SOURCE],
        "powertrain": [OWNER_MANUAL_SOURCE],
        "transmission": [PRICE_SOURCE],
        "body_style": [PRICE_SOURCE],
        "market": [PRICE_SOURCE],
        "model_year_from": [PRICE_SOURCE],
        "model_year_to": [PRICE_SOURCE],
    }
    if include_variant:
        field_sources["variant"] = [PRICE_SOURCE]
    return {
        "benchmark": BR_PATH.name,
        "benchmarkDatasetVersion": "br-1.0",
        "caseId": case_id,
        "side": side,
        "fieldSourceIds": field_sources,
        "evidenceBasis": {
            GENERATION_SOURCE: (
                "Retained Chevrolet product history establishes the current Onix as the second generation."
            ),
            PRICE_SOURCE: (
                "Retained Chevrolet MY25 price material establishes Onix Premier Turbo 116cv, "
                "hatch body, MY2025 and six-speed automatic transmission."
            ),
            OWNER_MANUAL_SOURCE: (
                "Official Chevrolet Onix 2025 owner manual identifies the 1.0 T engine, "
                "Etanol/Gasolina fuel capability and automatic-transmission configuration, "
                "supporting the benchmark's 1.0 turbo flex powertrain semantics without inference."
            ),
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


PROBE_MAPPINGS = (
    _mapping("br-match-onix-premier-turbo-my25", "left", include_variant=True),
    _mapping("br-match-onix-premier-turbo-my25", "right", include_variant=True),
    _mapping("br-review-onix-premier-missing-variant", "left", include_variant=True),
    _mapping("br-review-onix-premier-missing-variant", "right", include_variant=False),
)


def _augmented_br_benchmark(path: Path) -> None:
    payload = json.loads(BR_PATH.read_text(encoding="utf-8"))
    payload["sources"].append(
        {
            "id": OWNER_MANUAL_SOURCE,
            "publisher": "Chevrolet Brasil",
            "title": "Onix 2025 — Manual do Proprietário",
            "url": OWNER_MANUAL_URL,
            "supports": (
                "Official 2025 Onix specifications identify motor 1.0 T with Etanol/Gasolina "
                "fuel capability and automatic-transmission configurations for the hatch line."
            ),
        }
    )
    target_ids = {
        "br-match-onix-premier-turbo-my25",
        "br-review-onix-premier-missing-variant",
    }
    targets = [case for case in payload["cases"] if case["id"] in target_ids]
    if {case["id"] for case in targets} != target_ids:
        raise AssertionError("expected Onix MY25 cases were not resolved exactly")
    for case in targets:
        case["sourceIds"].append(OWNER_MANUAL_SOURCE)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _probe_records() -> list[dict]:
    overlay = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-onix-my25-1",
        "createdAt": "2026-09-01",
        "mappings": list(PROBE_MAPPINGS),
    }
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        br_path = root / BR_PATH.name
        overlay_path = root / "probe.json"
        _augmented_br_benchmark(br_path)
        overlay_path.write_text(json.dumps(overlay), encoding="utf-8")
        return build_multisource_operational_records(
            (Path(GLOBAL_PATH), br_path, Path(ADJACENT_PATH)),
            overlay_path,
        )


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class OnixMy25MultisourceProbeTests(unittest.TestCase):
    def test_probe_builds_all_four_my25_sides_with_official_flex_support(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 4)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        self.assertTrue(all(OWNER_MANUAL_SOURCE in record["sourceIds"] for record in records))

    def test_probe_replays_after_retained_corpus_with_complete_field_provenance(self) -> None:
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
