from datetime import datetime, timezone
from pathlib import Path
import unittest

from podium7.http_acquisition import (
    DirectHttpAcquisition,
    DirectHttpPolicy,
    HttpAcquisitionError,
    HttpAcquisitionErrorCode,
)
from podium7.public_web_acquisition_benchmark import (
    PublicWebSource,
    evaluate_public_web_acquisition,
    load_retained_public_web_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
AUTOEVOLUTION = ROOT / "benchmarks" / "web_extraction_source_family_corpus_v1.json"
FUELECONOMY = ROOT / "benchmarks" / "web_extraction_fueleconomy_source_family_v1.json"
FIXED_TIME = datetime(2026, 8, 23, 16, 45, tzinfo=timezone.utc)


class PublicWebAcquisitionBenchmarkTests(unittest.TestCase):
    def test_retained_inventory_is_derived_and_deduplicated(self) -> None:
        inventory, versions = load_retained_public_web_inventory(AUTOEVOLUTION, FUELECONOMY)

        self.assertEqual(len(inventory), 13)
        self.assertEqual(sum(len(source.case_ids) for source in inventory), 16)
        self.assertEqual(
            {family: sum(source.source_family == family for source in inventory) for family in versions},
            {"autoevolution": 9, "fueleconomy_gov": 4},
        )
        self.assertEqual(versions["autoevolution"], "autoevolution-source-family-1.0")
        self.assertEqual(versions["fueleconomy_gov"], "fueleconomy-find-a-car-source-family-1.0")
        self.assertTrue(all(source.source_url.startswith("https://") for source in inventory))
        vw = next(source for source in inventory if source.source_url.endswith("volkswagen-t-cross-2023.html"))
        self.assertEqual(vw.case_ids, ("vw-tcross-2023-1.0-5mt", "vw-tcross-2023-1.0-7at"))

    def test_report_aggregates_pass_and_explicit_failure_without_false_test_failure(self) -> None:
        sources = (
            PublicWebSource("family_a", "https://example.com/a", ("a",)),
            PublicWebSource("family_b", "https://example.com/b", ("b", "b2")),
        )

        def fake_acquire(url: str, policy: DirectHttpPolicy) -> DirectHttpAcquisition:
            self.assertEqual(policy.max_bytes, 1234)
            if url.endswith("/b"):
                raise HttpAcquisitionError(
                    HttpAcquisitionErrorCode.HTTP_STATUS,
                    url,
                    "unexpected HTTP status 403",
                    status=403,
                )
            return DirectHttpAcquisition(
                requested_url=url,
                final_url=url,
                redirect_count=0,
                status=200,
                content_type="text/html",
                charset="utf-8",
                body=b"ok",
                sha256="2689367b205c16ce32ed4200942b8b1e8e5e2c6f9b1a6f4df7b4f1a4c6f26f9",
            )

        report = evaluate_public_web_acquisition(
            sources,
            policy=DirectHttpPolicy(max_bytes=1234),
            acquire=fake_acquire,
            generated_at=FIXED_TIME,
            source_dataset_versions={"family_a": "v1", "family_b": "v2"},
        )
        metrics = report["metrics"]

        self.assertEqual(report["generatedAt"], FIXED_TIME.isoformat())
        self.assertEqual(metrics["totalUrlCount"], 2)
        self.assertEqual(metrics["representedCaseCount"], 3)
        self.assertEqual(metrics["passCount"], 1)
        self.assertEqual(metrics["failCount"], 1)
        self.assertEqual(metrics["successRate"], 0.5)
        self.assertEqual(metrics["failureCodes"], {"HTTP_STATUS": 1})
        self.assertEqual(metrics["bySourceFamily"]["family_a"]["successRate"], 1.0)
        self.assertEqual(metrics["bySourceFamily"]["family_b"]["successRate"], 0.0)
        failed = report["observations"][1]
        self.assertEqual(failed["status"], "FAIL")
        self.assertEqual(failed["httpStatus"], 403)
        self.assertEqual(failed["code"], "HTTP_STATUS")

    def test_unexpected_acquisition_exception_is_not_swallowed(self) -> None:
        source = PublicWebSource("family", "https://example.com/a", ("a",))

        def explode(url: str, policy: DirectHttpPolicy) -> DirectHttpAcquisition:
            raise AssertionError("unexpected implementation failure")

        with self.assertRaisesRegex(AssertionError, "unexpected implementation failure"):
            evaluate_public_web_acquisition((source,), acquire=explode, generated_at=FIXED_TIME)

    def test_inventory_rejects_duplicate_exact_url(self) -> None:
        sources = (
            PublicWebSource("family", "https://example.com/a", ("a",)),
            PublicWebSource("family", "https://example.com/a", ("b",)),
        )
        with self.assertRaisesRegex(ValueError, "duplicate exact URLs"):
            evaluate_public_web_acquisition(sources, generated_at=FIXED_TIME)

    def test_public_source_requires_fragment_free_https(self) -> None:
        for url in ("http://example.com/a", "https://example.com/a#fragment"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "fragment-free HTTPS"):
                    PublicWebSource("family", url, ("a",))

    def test_generated_at_must_be_timezone_aware(self) -> None:
        source = PublicWebSource("family", "https://example.com/a", ("a",))
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            evaluate_public_web_acquisition(
                (source,),
                acquire=lambda url, policy: DirectHttpAcquisition(
                    requested_url=url,
                    final_url=url,
                    redirect_count=0,
                    status=200,
                    content_type="text/html",
                    charset=None,
                    body=b"x",
                    sha256="x" * 64,
                ),
                generated_at=datetime(2026, 8, 23, 16, 45),
            )


if __name__ == "__main__":
    unittest.main()
