from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version as package_version
import json
from pathlib import Path
import platform
import sys
import tempfile
from time import perf_counter

from podium7.browser_acquisition_benchmark import (
    BrowserAcquisitionCode,
    BrowserAcquisitionError,
    BrowserNavigation,
    evaluate_browser_acquisition,
    load_retained_autoevolution_browser_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTOEVOLUTION = ROOT / "benchmarks" / "web_extraction_source_family_corpus_v1.json"
DEFAULT_FUELECONOMY = ROOT / "benchmarks" / "web_extraction_fueleconomy_source_family_v1.json"
DEFAULT_OUTPUT = ROOT / "artifacts" / "browser-acquisition-report.json"


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
        temporary.replace(path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _playwright_version() -> str:
    try:
        return package_version("playwright")
    except PackageNotFoundError as exc:
        raise RuntimeError(
            "Playwright is required only for this deliberate live characterization; "
            "install it explicitly before running this script"
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Measure controlled Chromium acquisition against retained Autoevolution URLs "
            "without stealth, proxying or user-agent impersonation."
        )
    )
    parser.add_argument("--autoevolution-dataset", type=Path, default=DEFAULT_AUTOEVOLUTION)
    parser.add_argument("--fueleconomy-dataset", type=Path, default=DEFAULT_FUELECONOMY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is required only for this deliberate live characterization; "
            "install it explicitly before running this script"
        ) from exc

    inventory, versions = load_retained_autoevolution_browser_inventory(
        args.autoevolution_dataset,
        args.fueleconomy_dataset,
    )
    timeout_ms = int(args.timeout_seconds * 1000)
    playwright_version = _playwright_version()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel="chromium")
        browser_version = browser.version

        def navigate(source_url: str) -> BrowserNavigation:
            context = browser.new_context()
            page = context.new_page()
            started = perf_counter()
            try:
                response = page.goto(
                    source_url,
                    wait_until="domcontentloaded",
                    timeout=timeout_ms,
                )
                if response is None:
                    raise BrowserAcquisitionError(
                        BrowserAcquisitionCode.NAVIGATION_ERROR,
                        "main-document navigation returned no response",
                    )
                title = page.title()
                body_text = page.locator("body").inner_text(timeout=5_000)
                html = page.content()
                elapsed_ms = int((perf_counter() - started) * 1000)
                return BrowserNavigation(
                    source_url=source_url,
                    final_url=page.url,
                    http_status=response.status,
                    title=title,
                    body_text=body_text,
                    html=html,
                    elapsed_ms=elapsed_ms,
                )
            except PlaywrightTimeoutError as exc:
                raise BrowserAcquisitionError(
                    BrowserAcquisitionCode.TIMEOUT,
                    f"navigation exceeded {args.timeout_seconds:g}s",
                ) from exc
            except PlaywrightError as exc:
                raise BrowserAcquisitionError(
                    BrowserAcquisitionCode.NAVIGATION_ERROR,
                    str(exc) or "Playwright navigation failed",
                ) from exc
            finally:
                context.close()

        report = evaluate_browser_acquisition(
            inventory,
            navigate=navigate,
            source_dataset_versions=versions,
            execution_metadata={
                "playwrightVersion": playwright_version,
                "browserName": "chromium",
                "browserVersion": browser_version,
                "channel": "chromium",
                "headless": True,
                "javascriptEnabled": True,
                "stealth": False,
                "proxy": False,
                "customUserAgent": False,
                "cookieSeeding": False,
                "challengeInteraction": False,
                "pythonVersion": platform.python_version(),
                "platform": platform.platform(),
            },
        )
        browser.close()

    _write_json_atomic(args.output, report)
    print(json.dumps(report["metrics"], sort_keys=True))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
