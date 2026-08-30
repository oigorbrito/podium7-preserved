import hashlib
import json
import unittest
from pathlib import Path

import pdfplumber

from podium7.inmetro_pbev_benchmark import (
    EXPECTED_TABLE_WIDTH,
    evaluate_inmetro_pbev_quantitative_benchmark,
    load_inmetro_pbev_quantitative_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_PATH = ROOT / "benchmarks" / "inmetro_pbev_quantitative_semantics_v1.json"
GOLD_PATH = ROOT / "benchmarks" / "inmetro_pbev_pdf_extraction_v1.json"


def _normalize(cell: str | None) -> str:
    return " ".join((cell or "").split())


class InmetroPbevQuantitativeBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.benchmark = load_inmetro_pbev_quantitative_benchmark(BENCHMARK_PATH)
        self.gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
        self.fixture_path = ROOT / self.gold["source"]["snapshotLocator"]

    def test_fixture_is_hash_bound_and_page_one_layout_is_28_columns(self) -> None:
        self.assertTrue(self.fixture_path.is_file())
        self.assertEqual(
            self.gold["source"]["rawContentSha256"],
            hashlib.sha256(self.fixture_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(615533, self.fixture_path.stat().st_size)
        self.assertEqual(1, self.gold["source"]["documentPage"])

        with pdfplumber.open(self.fixture_path) as document:
            page = document.pages[0]
            tables = page.extract_tables(
                table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
            )

        main_tables = [table for table in tables if table and max(len(row) for row in table) == EXPECTED_TABLE_WIDTH]
        self.assertTrue(main_tables)
        self.assertTrue(any(_normalize(row[0][0]) == "Categoria" for row in main_tables if row and row[0]))
        for table in main_tables:
            self.assertTrue(all(len(row) == EXPECTED_TABLE_WIDTH for row in table))

    def test_quantitative_benchmark_matches_real_page_one_rows(self) -> None:
        report = evaluate_inmetro_pbev_quantitative_benchmark(self.benchmark, self.fixture_path)
        metrics = report["metrics"]
        by_id = {case["id"]: case for case in report["cases"]}

        self.assertEqual("SOURCE_BOUND_QUANTITATIVE_BENCHMARK", report["status"])
        self.assertEqual("inmetro-pbev-2026-page1-quantitative-1.0", report["datasetVersion"])
        self.assertEqual(4, metrics["caseCount"])
        self.assertEqual(4, metrics["matchedCaseCount"])
        self.assertGreater(metrics["valueCellCount"], metrics["placeholderCellCount"])
        self.assertGreater(metrics["placeholderCoverage"], 0.0)

        expected_columns = {
            case.id: {str(column): expectation for column, expectation in case.expected_columns}
            for case in self.benchmark.cases
        }

        with pdfplumber.open(self.fixture_path) as document:
            page = document.pages[0]
            tables = page.extract_tables(
                table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
            )
        rows = [
            tuple(_normalize(cell) for cell in row)
            for table in tables
            if table and max(len(row) for row in table) == EXPECTED_TABLE_WIDTH
            for row in table
        ]

        for case in self.benchmark.cases:
            identity = case.identity
            matches = [
                row
                for row in rows
                if row[:10]
                == (
                    identity.category,
                    identity.make,
                    identity.model,
                    identity.version,
                    identity.engine,
                    identity.propulsion,
                    identity.transmission,
                    identity.air_conditioning,
                    identity.steering_assist,
                    identity.fuel,
                )
            ]
            self.assertEqual(1, len(matches), case.id)
            row = matches[0]

            # Structural identity never depends on the quantitative cells.
            self.assertEqual(identity.make, row[1])
            self.assertEqual(identity.model, row[2])

            for column_text, expectation in expected_columns[case.id].items():
                column = int(column_text)
                actual = row[column]
                self.assertEqual(expectation.state, "PLACEHOLDER" if actual == "\\" else "VALUE")
                if expectation.state == "PLACEHOLDER":
                    self.assertEqual("\\", actual)
                    continue

                self.assertEqual(expectation.raw, actual)
                if expectation.kind == "number":
                    self.assertEqual(float(expectation.value), float(actual))
                else:
                    self.assertEqual(expectation.value, actual)

            if case.id == "pbev-2026-p1-byd-dolphin-mini-gs-ev":
                self.assertEqual("\\", row[17])
                self.assertEqual("\\", row[20])
                self.assertEqual("58.6", row[21])
                self.assertEqual("41.9", row[22])
                self.assertEqual("0.41", row[23])
                self.assertEqual("280", row[24])
                self.assertEqual("A", row[25])
                self.assertEqual("A", row[26])
            elif case.id == "pbev-2026-p1-fiat-500e-icon":
                self.assertEqual("\\", row[17])
                self.assertEqual("\\", row[20])
                self.assertEqual("47.3", row[21])
                self.assertEqual("40.4", row[22])
                self.assertEqual("0.46", row[23])
                self.assertEqual("227", row[24])
            elif case.id == "pbev-2026-p1-fiat-mobi-trekking":
                self.assertEqual("9.8", row[17])
                self.assertEqual("10.6", row[18])
                self.assertEqual("14.0", row[19])
                self.assertEqual("15.1", row[20])
                self.assertEqual("\\", row[21])
                self.assertEqual("\\", row[22])
                self.assertEqual("1.46", row[23])
                self.assertEqual("\\", row[24])
                self.assertEqual("0", row[14])
                self.assertEqual("\\", row[16])
            elif case.id == "pbev-2026-p1-peugeot-208-gt-hybrid":
                self.assertEqual("9.1", row[17])
                self.assertEqual("9.6", row[18])
                self.assertEqual("13.0", row[19])
                self.assertEqual("13.8", row[20])
                self.assertEqual("\\", row[21])
                self.assertEqual("\\", row[22])
                self.assertEqual("1.60", row[23])
                self.assertEqual("\\", row[24])

    def test_existing_observation_limitations_remain_explicit(self) -> None:
        self.assertFalse(self.benchmark.identity_boundary["quantitativeFactsParticipateInIdentityResolution"])
        self.assertEqual("10-16", self.benchmark.blocked_columns[0]["range"])
        self.assertIn("exact individual header semantics", self.benchmark.blocked_columns[0]["reason"])


if __name__ == "__main__":
    unittest.main()
