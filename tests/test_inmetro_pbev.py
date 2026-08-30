import unittest
from types import SimpleNamespace
from unittest.mock import patch

from podium7.http_acquisition import HttpAcquisitionError, HttpAcquisitionErrorCode
from podium7.inmetro_pbev import (
    acquire_inmetro_pbev_pdf,
    extract_inmetro_pbev_pdf,
    extract_inmetro_pbev_tables,
    inmetro_pdf_policy,
)


class InmetroPbevTests(unittest.TestCase):
    def test_source_specific_policy_allows_only_pdf(self):
        policy = inmetro_pdf_policy()
        self.assertEqual(("application/pdf",), policy.allowed_content_types)
        self.assertEqual(("https",), policy.allowed_schemes)
        self.assertEqual(2_000_000, policy.max_bytes)

    def test_acquisition_rejects_non_inmetro_host_before_network(self):
        with self.assertRaises(HttpAcquisitionError) as caught:
            acquire_inmetro_pbev_pdf("https://example.com/pbev.pdf")
        self.assertEqual(HttpAcquisitionErrorCode.INVALID_URL, caught.exception.code)

    def test_table_parser_handles_multiline_header_and_preserves_source_coordinates(self):
        table = [
            ["Categoria", "Marca", "Modelo", "Versão", "Motor", "Tipo de", "Transmissão", "Combustível"],
            [None, None, None, None, None, "Propulsão", "Velocidades (nº)", None],
            ["Sub Compacto", "FIAT", "MOBI", "TREKKING", "1.0-6V", "Combustão", "M-5", "F"],
            ["Compacto", "PEUGEOT", "E-208", "GT ELÉTRICO", "Elétrico", "Elétrico", "A-1", "E"],
        ]
        records = extract_inmetro_pbev_tables([table], "https://www.gov.br/inmetro/pbev.pdf", page_number=3)
        self.assertEqual(2, len(records))
        self.assertEqual("FIAT", records[0].make)
        self.assertEqual("MOBI", records[0].model)
        self.assertEqual("TREKKING", records[0].version)
        self.assertEqual("Combustão", records[0].propulsion)
        self.assertEqual("M-5", records[0].transmission)
        self.assertEqual("F", records[0].fuel)
        self.assertEqual(3, records[0].page_number)
        self.assertEqual(3, records[0].row_number)

    def test_table_parser_ignores_unrecognized_tables_and_empty_identity_rows(self):
        noise = [["foo", "bar"], ["x", "y"]]
        table = [
            ["Categoria", "Marca", "Modelo", "Versão", "Motor", "Tipo de Propulsão", "Transmissão", "Combustível"],
            ["Compacto", "", "", "", "", "", "", ""],
        ]
        self.assertEqual((), extract_inmetro_pbev_tables([noise, table], "https://www.gov.br/inmetro/pbev.pdf"))

    def test_pdf_wrapper_rejects_non_pdf_before_loading_dependency(self):
        with patch("podium7.inmetro_pbev.importlib.import_module") as loader:
            with self.assertRaisesRegex(ValueError, "not a PDF"):
                extract_inmetro_pbev_pdf(b"not-pdf", "https://www.gov.br/inmetro/pbev.pdf")
            loader.assert_not_called()

    def test_pdf_wrapper_reports_missing_runtime_dependency(self):
        with patch("podium7.inmetro_pbev.importlib.import_module", side_effect=ModuleNotFoundError("pdfplumber")):
            with self.assertRaisesRegex(RuntimeError, "pdfplumber is required"):
                extract_inmetro_pbev_pdf(b"%PDF-fake", "https://www.gov.br/inmetro/pbev.pdf")

    def test_pdf_wrapper_fails_when_no_vehicle_rows_are_recognized(self):
        class Page:
            def extract_tables(self, table_settings=None):
                return [[['noise']]]

        class Document:
            pages = [Page()]
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False

        fake_pdfplumber = SimpleNamespace(open=lambda _: Document())
        with patch("podium7.inmetro_pbev.importlib.import_module", return_value=fake_pdfplumber):
            with self.assertRaisesRegex(ValueError, "no recognized vehicle table rows"):
                extract_inmetro_pbev_pdf(b"%PDF-fake", "https://www.gov.br/inmetro/pbev.pdf")


if __name__ == "__main__":
    unittest.main()
