from dataclasses import replace
import json
from pathlib import Path
import re
import unittest

from podium7.catalog import CatalogMatchOutcome, CatalogVehicleIdentity
from podium7.catalog_benchmark import CatalogBenchmarkCase, CatalogBenchmarkDataset
from podium7.catalog_heterogeneity_adapter import compare_catalog_heterogeneity


_TRANSMISSION_HYPHEN_CODE = re.compile(r"^([A-Za-z]+)-(\d+)$")
_GOLD_PATH = Path("benchmarks/inmetro_pbev_pdf_extraction_v1.json")


def _normalize_transmission_code(value: str | None) -> str | None:
    if value is None:
        return None
    match = _TRANSMISSION_HYPHEN_CODE.fullmatch(value.strip())
    if match is None:
        return value
    return f"{match.group(1)}{match.group(2)}"


def _candidate_identity(identity: CatalogVehicleIdentity) -> CatalogVehicleIdentity:
    return replace(
        identity,
        transmission=_normalize_transmission_code(identity.transmission),
    )


def _candidate_dataset(dataset: CatalogBenchmarkDataset) -> CatalogBenchmarkDataset:
    return CatalogBenchmarkDataset(
        version=f"{dataset.version}-transmission-code-candidate",
        source_ids=dataset.source_ids,
        cases=tuple(
            CatalogBenchmarkCase(
                id=case.id,
                expected=case.expected,
                left=_candidate_identity(case.left),
                right=_candidate_identity(case.right),
                source_ids=case.source_ids,
                rationale=case.rationale,
            )
            for case in dataset.cases
        ),
    )


def _dataset(
    version: str,
    right_identity: CatalogVehicleIdentity,
    *,
    expected: CatalogMatchOutcome = CatalogMatchOutcome.MATCH,
    left_identity: CatalogVehicleIdentity | None = None,
) -> CatalogBenchmarkDataset:
    left = left_identity or CatalogVehicleIdentity(
        make="Ford",
        model="Mustang",
        generation="S650",
        variant="Dark Horse",
        powertrain="5.0 V8",
        transmission="M-6",
        body_style="Coupe",
        market="US",
    )
    return CatalogBenchmarkDataset(
        version=version,
        source_ids=("stress-fixture",),
        cases=(
            CatalogBenchmarkCase(
                id="paired-case",
                expected=expected,
                left=left,
                right=right_identity,
                source_ids=("stress-fixture",),
                rationale="controlled heterogeneity stress fixture",
            ),
        ),
    )


class TransmissionRepresentationCandidateTests(unittest.TestCase):
    def test_candidate_syntax_is_bounded_by_retained_inmetro_codes(self) -> None:
        payload = json.loads(_GOLD_PATH.read_text(encoding="utf-8"))
        retained = {case["expected"]["transmission"] for case in payload["cases"]}
        self.assertEqual({"N.A.", "A-1", "M-5"}, retained)
        self.assertEqual("A1", _normalize_transmission_code("A-1"))
        self.assertEqual("M5", _normalize_transmission_code("M-5"))
        self.assertEqual("N.A.", _normalize_transmission_code("N.A."))

    def test_hyphen_code_candidate_recovers_representation_recall_without_false_merge(self) -> None:
        clean = _dataset(
            "clean",
            CatalogVehicleIdentity(
                make="FORD",
                model="MUSTANG",
                generation="s650",
                variant="dark horse",
                powertrain="V8 5.0",
                transmission="M-6",
                body_style="coupe",
                market="us",
            ),
        )
        heterogeneous = _dataset(
            "heterogeneous",
            CatalogVehicleIdentity(
                make="FORD",
                model="MUSTANG",
                generation="s650",
                variant="dark horse",
                powertrain="V8 5.0",
                transmission="M6",
                body_style="coupe",
                market="us",
            ),
        )

        report = compare_catalog_heterogeneity(
            _candidate_dataset(clean),
            {"representation-transmission": _candidate_dataset(heterogeneous)},
        )
        item = report["slices"][0]
        self.assertEqual(0.0, item["deltas"]["recallDelta"])
        self.assertEqual(0.0, item["deltas"]["missedMatchDelta"])
        self.assertEqual(0.0, item["deltas"]["falseMergeDelta"])
        self.assertFalse(item["safetyRegression"])

    def test_candidate_does_not_reinterpret_regulatory_variant_as_retail_trim(self) -> None:
        left = CatalogVehicleIdentity(
            make="Volkswagen",
            model="Golf",
            generation="8",
            variant="Highline",
            powertrain="1.5 TSI",
            transmission="DCT-7",
            body_style="Hatchback",
            market="EU",
            model_year_from=2026,
            model_year_to=2026,
        )
        clean = _dataset(
            "clean-semantic",
            CatalogVehicleIdentity(
                make="Volkswagen",
                model="Golf",
                generation="8",
                variant="Highline",
                powertrain="1.5 TSI",
                transmission="DCT-7",
                body_style="Hatchback",
                market="EU",
            ),
            expected=CatalogMatchOutcome.REVIEW,
            left_identity=left,
        )
        heterogeneous = _dataset(
            "bad-regulatory-projection",
            CatalogVehicleIdentity(
                make="Volkswagen",
                model="Golf",
                generation="8",
                variant="TYPE-VARIANT-VERSION-X",
                powertrain="1.5 TSI",
                transmission="DCT-7",
                body_style="Hatchback",
                market="EU",
            ),
            expected=CatalogMatchOutcome.REVIEW,
            left_identity=left,
        )

        report = compare_catalog_heterogeneity(
            _candidate_dataset(clean),
            {"regulatory-to-retail-variant": _candidate_dataset(heterogeneous)},
        )
        item = report["slices"][0]
        self.assertEqual(1.0, item["deltas"]["ambiguousOvercommitDelta"])
        self.assertTrue(item["safetyRegression"])


if __name__ == "__main__":
    unittest.main()
