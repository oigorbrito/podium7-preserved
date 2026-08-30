import unittest
from pathlib import Path

from podium7.inmetro_pbev_benchmark import (
    evaluate_inmetro_pbev_quantitative_benchmark,
    load_inmetro_pbev_quantitative_benchmark,
)


DATASET = (
    Path(__file__).resolve().parents[1]
    / "benchmarks"
    / "inmetro_pbev_quantitative_semantics_v1.json"
)


class InmetroPbevQuantitativeBenchmarkTests(unittest.TestCase):
    def test_quantitative_benchmark_is_source_backed_and_balanced(self) -> None:
        benchmark = load_inmetro_pbev_quantitative_benchmark(DATASET)

        self.assertEqual(benchmark.version, "inmetro-pbev-quantitative-semantics-1.0")
        self.assertEqual(benchmark.artifact, "INMETRO_PBEV_QUANTITATIVE_SEMANTICS_V1")
        self.assertEqual(len(benchmark.cases), 4)
        self.assertEqual(
            [case.identity.propulsion for case in benchmark.cases],
            ["Elétrico", "Elétrico", "Combustão", "Híbrido"],
        )
        self.assertTrue(all(case.source_url.startswith("https://www.gov.br/inmetro/") for case in benchmark.cases))
        self.assertTrue(all(case.source_excerpt.strip() for case in benchmark.cases))
        self.assertTrue(all(case.expected_missing == ("emissions.tailpipeCo2Gkm", "emissions.tailpipeCo2eGkm", "consumption.cityKmL", "consumption.roadKmL") for case in benchmark.cases[:2]))

    def test_quantitative_benchmark_metrics_capture_units_and_missingness(self) -> None:
        benchmark = load_inmetro_pbev_quantitative_benchmark(DATASET)
        report = evaluate_inmetro_pbev_quantitative_benchmark(benchmark)
        metrics = report["metrics"]
        cases = {case["id"]: case for case in report["cases"]}

        self.assertEqual(report["totalCases"], 4)
        self.assertEqual(metrics["electricCaseCount"], 2)
        self.assertEqual(metrics["combustionCaseCount"], 1)
        self.assertEqual(metrics["hybridCaseCount"], 1)
        self.assertEqual(metrics["numericMeasurementCount"], 20)
        self.assertEqual(metrics["numericMissingCount"], 8)
        self.assertEqual(metrics["gradeObservationCount"], 8)
        self.assertEqual(metrics["completeCaseCount"], 4)
        self.assertEqual(metrics["numericCoverage"], 20 / 28)

        self.assertEqual(cases["fiat-500e-icon"]["numericMissing"], 4)
        self.assertEqual(cases["fiat-mobi-trekking"]["numericPresent"], 7)
        self.assertEqual(cases["peugeot-208-gt-hybrid"]["gradePresent"], 2)
        self.assertEqual(cases["byd-dolphin-mini-gs-ev"]["sourceReference"], "P0:L56")


if __name__ == "__main__":
    unittest.main()
