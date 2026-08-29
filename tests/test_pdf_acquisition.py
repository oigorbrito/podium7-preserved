import hashlib
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from podium7.http_acquisition import (
    DirectHttpAcquisition,
    DirectHttpPolicy,
    HttpAcquisitionError,
    HttpAcquisitionErrorCode,
)
from podium7.pdf_acquisition import (
    PDF_MEDIA_TYPE,
    PdfAcquisitionContract,
    acquire_and_freeze_pdf,
    acquire_pdf,
    pdf_http_policy,
)


class PdfAcquisitionTests(unittest.TestCase):
    def contract(self):
        return PdfAcquisitionContract(
            source_id="inmetro_pbev",
            locator="https://www.gov.br/inmetro/table.pdf",
            max_bytes=1_000_000,
        )

    def acquisition(self, *, final_url=None, content_type=PDF_MEDIA_TYPE):
        body = b"%PDF-1.7 fixture"
        locator = self.contract().locator
        return DirectHttpAcquisition(
            requested_url=locator,
            final_url=final_url or locator,
            redirect_count=0 if final_url in (None, locator) else 1,
            status=200,
            content_type=content_type,
            charset=None,
            body=body,
            sha256=hashlib.sha256(body).hexdigest(),
        )

    def test_pdf_profile_is_explicit_and_does_not_change_default_policy(self):
        policy = pdf_http_policy(self.contract())
        self.assertEqual((PDF_MEDIA_TYPE,), policy.allowed_content_types)
        self.assertEqual(0, policy.max_redirects)
        self.assertEqual(("https",), policy.allowed_schemes)
        self.assertFalse(policy.allow_private_network)
        self.assertNotIn(PDF_MEDIA_TYPE, DirectHttpPolicy().allowed_content_types)

    def test_exact_pdf_acquisition_preserves_existing_http_result(self):
        item = self.acquisition()
        with patch("podium7.pdf_acquisition.acquire_http", return_value=item) as mocked:
            result = acquire_pdf(self.contract())
        self.assertEqual(item, result)
        mocked.assert_called_once()
        self.assertEqual((PDF_MEDIA_TYPE,), mocked.call_args.args[1].allowed_content_types)
        self.assertEqual(0, mocked.call_args.args[1].max_redirects)

    def test_redirected_final_locator_fails_closed(self):
        item = self.acquisition(final_url="https://www.gov.br/inmetro/other.pdf")
        with patch("podium7.pdf_acquisition.acquire_http", return_value=item):
            with self.assertRaisesRegex(
                HttpAcquisitionError,
                "exact requested and final locator identity",
            ) as caught:
                acquire_pdf(self.contract())
        self.assertEqual(HttpAcquisitionErrorCode.INVALID_URL, caught.exception.code)

    def test_non_pdf_response_fails_closed_even_if_transport_is_stubbed(self):
        item = self.acquisition(content_type="text/html")
        with patch("podium7.pdf_acquisition.acquire_http", return_value=item):
            with self.assertRaisesRegex(
                HttpAcquisitionError,
                "expected 'application/pdf'",
            ) as caught:
                acquire_pdf(self.contract())
        self.assertEqual(HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_TYPE, caught.exception.code)

    def test_freeze_reuses_verified_snapshot_path(self):
        item = self.acquisition()
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "pbev.pdf"
            with patch("podium7.pdf_acquisition.acquire_http", return_value=item):
                frozen = acquire_and_freeze_pdf(self.contract(), destination)
            self.assertEqual(item.body, destination.read_bytes())
            self.assertIn(item.sha256, frozen.content_ref)

    def test_invalid_contract_values_fail_closed(self):
        with self.assertRaises(ValueError):
            PdfAcquisitionContract(source_id="", locator="https://example.com/a.pdf")
        with self.assertRaises(ValueError):
            PdfAcquisitionContract(source_id="x", locator="http://example.com/a.pdf")
        with self.assertRaises(ValueError):
            PdfAcquisitionContract(source_id="x", locator="https://example.com/a.pdf#fragment")
        with self.assertRaises(ValueError):
            PdfAcquisitionContract(source_id="x", locator="https://example.com/a.pdf", max_bytes=True)
        for value in (math.nan, math.inf, -math.inf, 0):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite positive"):
                    PdfAcquisitionContract(
                        source_id="x",
                        locator="https://example.com/a.pdf",
                        timeout_seconds=value,
                    )


if __name__ == "__main__":
    unittest.main()
