from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import unittest

from podium7.browser_acquisition_benchmark import (
    BrowserAcquisitionCode,
    BrowserAcquisitionError,
    BrowserNavigation,
    MIN_RELEVANCE_MARKERS,
    evaluate_browser_acquisition,
    load_retained_autoevolution_browser_inventory,
)
from podium7.public_web_acquisition_benchmark import PublicWebSource


ROOT = Path(__file__).resolve().parents[1]
AUTOEVOLUTION = ROOT / "benchmarks" / "web_extraction_source_family_corpus_v1.json"
FUELECONOMY = ROOT / "benchmarks" / "web_extraction_fueleconomy_source_family_v1.json"


def source(url: str = "https://www.autoevolution.com/cars/example.html") -> PublicWebSource:
    return PublicWebSource("autoevolution", url, ("case-1",))


def navigation(
    url: str = "https://www.autoevolution.com/cars/example.html",
    *,
    status: int = 200,
    body: str | None = None,
    html: str | None = None,
    elapsed_ms: int = 125,
) -> BrowserNavigation:
    relevant = "Displacement Power Torque Fuel System Drive Type Gearbox Wheelbase"
    body_text = relevant if body is None else body
    return BrowserNavigation(
        source_url=url,
        final_url=url,
        http_status=status,
        title="Example vehicle specifications",
        body_text=body_text,
        html=html if html is not None else f"<html><body>{body_text}</body></html>",
        elapsed_ms=elapsed_ms,
    )


class BrowserAcquisitionBenchmarkTests(unittest.TestCase):
    def test_retained_inventory_is_exact_nine_url_autoevolution_slice(self) -> None:
        inventory, versions = load_retained_autoevolution_browser_inventory(
            AUTOEVOLUTION,
            FUELECONOMY,
        )
        self.assertEqual(9, len(inventory))
        self.assertEqual(12, sum(len(item.case_ids) for item in inventory))
        self.assertEqual({"autoevolution"}, {item.source_family for item in inventory})
        self.assertEqual(9, len({item.source_url for item in inventory}))
        self.assertEqual("autoevolution-source-family-1.0", versions["autoevolution"])

    def test_relevant_2xx_body_passes_conservatively(self) -> None:
        report = evaluate_browser_acquisition(
            (source(),),
            navigate=lambda url: navigation(url),
            generated_at=datetime(2026, 8, 23, tzinfo=timezone.utc),
        )
        self.assertEqual(1, report["metrics"]["passCount"])
        observation = report["observations"][0]
        self.assertEqual("PASS", observation["status"])
        self.assertIsNone(observation["code"])
        self.assertGreaterEqual(len(observation["relevanceMarkers"]), MIN_RELEVANCE_MARKERS)
        self.assertEqual(64, len(observation["bodySha256"]))
        self.assertEqual(64, len(observation["htmlSha256"]))

    def test_non_2xx_is_http_status_failure_even_with_block_text(self) -> None:
        report = evaluate_browser_acquisition(
            (source(),),
            navigate=lambda url: navigation(url, status=403, body="Access Denied Forbidden"),
        )
        observation = report["observations"][0]
        self.assertEqual("FAIL", observation["status"])
        self.assertEqual("HTTP_STATUS", observation["code"])
        self.assertIn("access denied", observation["blockIndicators"])
        self.assertEqual({"HTTP_STATUS": 1}, report["metrics"]["failureCodes"])

    def test_2xx_challenge_page_is_not_false_pass(self) -> None:
        report = evaluate_browser_acquisition(
            (source(),),
            navigate=lambda url: navigation(
                url,
                body="Verify you are human. Security check. Displacement Power Torque Fuel System.",
            ),
        )
        observation = report["observations"][0]
        self.assertEqual("FAIL", observation["status"])
        self.assertEqual("BLOCK_PAGE", observation["code"])
        self.assertIn("verify you are human", observation["blockIndicators"])

    def test_insufficient_relevance_is_explicit_failure(self) -> None:
        report = evaluate_browser_acquisition(
            (source(),),
            navigate=lambda url: navigation(url, body="Vehicle news and photos. Power."),
        )
        observation = report["observations"][0]
        self.assertEqual("INSUFFICIENT_RELEVANCE", observation["code"])
        self.assertEqual(0, report["metrics"]["passCount"])

    def test_empty_body_is_explicit_failure(self) -> None:
        report = evaluate_browser_acquisition(
            (source(),),
            navigate=lambda url: navigation(url, body=""),
        )
        self.assertEqual("EMPTY_BODY", report["observations"][0]["code"])

    def test_expected_browser_timeout_is_measurement_data(self) -> None:
        def timeout(_url: str) -> BrowserNavigation:
            raise BrowserAcquisitionError(BrowserAcquisitionCode.TIMEOUT, "navigation exceeded 20s")

        report = evaluate_browser_acquisition((source(),), navigate=timeout)
        self.assertEqual("TIMEOUT", report["observations"][0]["code"])
        self.assertEqual(0, report["metrics"]["measuredNavigationCount"])
        self.assertIsNone(report["metrics"]["meanNavigationElapsedMs"])

    def test_unexpected_navigation_exception_is_not_swallowed(self) -> None:
        def broken(_url: str) -> BrowserNavigation:
            raise RuntimeError("implementation bug")

        with self.assertRaisesRegex(RuntimeError, "implementation bug"):
            evaluate_browser_acquisition((source(),), navigate=broken)

    def test_generated_at_must_be_timezone_aware(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            evaluate_browser_acquisition(
                (source(),),
                navigate=lambda url: navigation(url),
                generated_at=datetime(2026, 8, 23, 12, 0, 0),
            )

    def test_navigator_cannot_return_result_for_different_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "wrong source URL"):
            evaluate_browser_acquisition(
                (source(),),
                navigate=lambda _url: navigation("https://www.autoevolution.com/cars/other.html"),
            )


if __name__ == "__main__":
    unittest.main()
