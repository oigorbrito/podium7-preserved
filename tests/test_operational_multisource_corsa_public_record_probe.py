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


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATHS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
RETAINED_ATTRIBUTION_PATH = ROOT / "benchmarks" / "operational_multisource_field_attribution_v1.json"
FIPE_SOURCE = "fipe-official-vehicle-index"
TCE_MODEL_SOURCE = "tce-pr-fipe-model-table-2015"
DETRAN_1995_SOURCE = "detran-rr-leilao-004-2025-corsa-1995"
DETRAN_1997_SOURCE = "detran-rr-leilao-003-2025-corsa-1997"
PROBE_KEYS = (
    ("br-1.0", "br-no-match-corsa-shared-fipe-different-model-year", "left"),
    ("br-1.0", "br-no-match-corsa-shared-fipe-different-model-year", "right"),
    ("br-1.0", "br-review-shared-fipe-code-alone", "left"),
    ("br-1.0", "br-review-shared-fipe-code-alone", "right"),
)


def _augmented_br_benchmark(directory: Path) -> Path:
    payload = json.loads(ACTIVE_PATHS[1].read_text(encoding="utf-8"))
    payload["sources"].extend(
        [
            {
                "id": TCE_MODEL_SOURCE,
                "publisher": "Tribunal de Contas do Estado do Parana",
                "title": "Anexo II - Tabela Padrao de Modelos - FIPE 2015",
                "url": "https://www.tce.pr.gov.br/data/files/BF/44/F8/6D/FF9049108A198F3924D419A8/Anexo%20II%20-%20Tabela%20Padrao%20de%20Modelos%20-%20FIPE%202015.pdf",
                "supports": "Official public-administration model table maps FIPE model code 0040010 to GM-Chevrolet Corsa Wind 1.0 MPFI / EFI 2p.",
            },
            {
                "id": DETRAN_1995_SOURCE,
                "publisher": "Departamento Estadual de Transito de Roraima",
                "title": "Edital de Leilao No 004/2025/DETRAN-RR",
                "url": "https://www.detran.rr.gov.br/wp-content/uploads/2025/09/EDITAL-DE-LEILAO-No-004-2025-DETRAN-RR.pdf",
                "supports": "Official DETRAN-RR public record lists Chevrolet Corsa Wind 1.0 EFI, 1995/1995, with FIPE code 004001-0.",
            },
            {
                "id": DETRAN_1997_SOURCE,
                "publisher": "Departamento Estadual de Transito de Roraima",
                "title": "Edital de Leilao No 003/2025/DETRAN-RR",
                "url": "https://www.detran.rr.gov.br/wp-content/uploads/2025/06/EDITAL-DE-LEILAO-No-003-2025-DETRAN-RR_compressed-1.pdf",
                "supports": "Official DETRAN-RR public record lists Chevrolet Corsa Wind 1.0 MPFI, 1997/1997, under the same FIPE model-code family documented by the public model table.",
            },
        ]
    )
    path = directory / "catalog_identity_golden_br_v1.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _year_mapping(side: str, year: int, detran_source: str) -> dict:
    return {
        "benchmark": "catalog_identity_golden_br_v1.json",
        "benchmarkDatasetVersion": "br-1.0",
        "caseId": "br-no-match-corsa-shared-fipe-different-model-year",
        "side": side,
        "fieldSourceIds": {
            "make": [TCE_MODEL_SOURCE],
            "model": [TCE_MODEL_SOURCE],
            "market": [FIPE_SOURCE],
            "model_year_from": [detran_source],
            "model_year_to": [detran_source],
            "external_identifiers": [TCE_MODEL_SOURCE, detran_source],
        },
        "evidenceBasis": {
            FIPE_SOURCE: "Retained FIPE official evidence defines national vehicle lookup semantics and model-year-specific FIPE-code lookup.",
            TCE_MODEL_SOURCE: "Official TCE-PR administrative model table maps code 0040010 to GM-Chevrolet Corsa Wind 1.0 MPFI / EFI 2p.",
            detran_source: f"Official DETRAN-RR vehicle record establishes the Corsa Wind observation in model year {year} and preserves the public-record link to FIPE code 004001-0.",
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


def _review_mapping(side: str) -> dict:
    return {
        "benchmark": "catalog_identity_golden_br_v1.json",
        "benchmarkDatasetVersion": "br-1.0",
        "caseId": "br-review-shared-fipe-code-alone",
        "side": side,
        "fieldSourceIds": {
            "make": [TCE_MODEL_SOURCE],
            "model": [TCE_MODEL_SOURCE],
            "market": [FIPE_SOURCE],
            "external_identifiers": [TCE_MODEL_SOURCE, DETRAN_1995_SOURCE],
        },
        "evidenceBasis": {
            FIPE_SOURCE: "Retained FIPE official evidence defines the identifier as supporting, model-year-specific lookup evidence rather than sole catalog identity authority.",
            TCE_MODEL_SOURCE: "Official TCE-PR administrative model table maps code 0040010 to GM-Chevrolet Corsa Wind 1.0 MPFI / EFI 2p.",
            DETRAN_1995_SOURCE: "Official DETRAN-RR record independently uses formatted code 004001-0 for a Chevrolet Corsa Wind observation.",
        },
        "status": "PROBE_ONLY_NOT_RETAINED",
    }


def _overlay(directory: Path) -> Path:
    payload = {
        "schema": "podium7.catalog-operational-field-attribution.v1",
        "datasetVersion": "probe-corsa-public-record-1",
        "createdAt": "2026-09-01",
        "mappings": [
            _year_mapping("left", 1995, DETRAN_1995_SOURCE),
            _year_mapping("right", 1997, DETRAN_1997_SOURCE),
            _review_mapping("left"),
            _review_mapping("right"),
        ],
    }
    path = directory / "probe.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _probe_records() -> list[dict]:
    with tempfile.TemporaryDirectory() as raw_directory:
        directory = Path(raw_directory)
        augmented_br = _augmented_br_benchmark(directory)
        overlay = _overlay(directory)
        paths = (ACTIVE_PATHS[0], augmented_br, ACTIVE_PATHS[2])
        return build_multisource_operational_records(paths, overlay)


def _key(record: dict) -> tuple[str, str, str]:
    return (record["datasetVersion"], record["caseId"], record["side"])


class CorsaPublicRecordMultisourceProbeTests(unittest.TestCase):
    def test_probe_builds_exact_four_corsa_sides_without_secondary_source(self) -> None:
        records = _probe_records()
        self.assertEqual(len(records), 4)
        self.assertEqual(tuple(_key(record) for record in records), PROBE_KEYS)
        for record in records:
            self.assertNotIn("corsa-wind-fipe-code-secondary", record["sourceIds"])
            self.assertGreaterEqual(len(record["sourceIds"]), 2)

    def test_probe_replays_after_current_retained_corpus_with_exact_provenance(self) -> None:
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
            self.assertEqual(actual_bindings, expected_bindings)


if __name__ == "__main__":
    unittest.main()
