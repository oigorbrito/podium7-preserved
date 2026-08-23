from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
from pathlib import Path
from typing import Callable, Iterable, Mapping
from urllib.parse import urlsplit

from .public_web_acquisition_benchmark import (
    PublicWebSource,
    load_retained_public_web_inventory,
)


REPORT_SCHEMA = "podium7.browser-acquisition-characterization.v1"
INVENTORY_VERSION = "retained-autoevolution-browser-urls-1.0"
AUTOEVOLUTION_FAMILY = "autoevolution"
MIN_RELEVANCE_MARKERS = 4
RELEVANCE_MARKERS = (
    "displacement",
    "power",
    "torque",
    "fuel system",
    "drive type",
    "gearbox",
    "wheelbase",
    "unladen weight",
    "combined",
)
BLOCK_INDICATORS = (
    "access denied",
    "attention required",
    "captcha",
    "checking your browser",
    "cloudflare",
    "forbidden",
    "request blocked",
    "security check",
    "verify you are human",
)


class BrowserAcquisitionCode(str, Enum):
    HTTP_STATUS = "HTTP_STATUS"
    EMPTY_BODY = "EMPTY_BODY"
    BLOCK_PAGE = "BLOCK_PAGE"
    INSUFFICIENT_RELEVANCE = "INSUFFICIENT_RELEVANCE"
    TIMEOUT = "TIMEOUT"
    NAVIGATION_ERROR = "NAVIGATION_ERROR"


class BrowserAcquisitionError(RuntimeError):
    def __init__(self, code: BrowserAcquisitionCode, detail: str) -> None:
        if not isinstance(code, BrowserAcquisitionCode):
            raise TypeError("code must be BrowserAcquisitionCode")
        if not isinstance(detail, str) or not detail.strip():
            raise ValueError("detail must be non-empty text")
        super().__init__(detail)
        self.code = code
        self.detail = detail.strip()


@dataclass(frozen=True)
class BrowserNavigation:
    source_url: str
    final_url: str
    http_status: int
    title: str
    body_text: str
    html: str
    elapsed_ms: int

    def __post_init__(self) -> None:
        for name, value in (("source_url", self.source_url), ("final_url", self.final_url)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty text")
            parsed = urlsplit(value)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                raise ValueError(f"{name} must be an absolute HTTP(S) URL")
        if isinstance(self.http_status, bool) or not isinstance(self.http_status, int):
            raise TypeError("http_status must be an integer")
        if self.http_status < 100 or self.http_status > 599:
            raise ValueError("http_status must be between 100 and 599")
        if not isinstance(self.title, str):
            raise TypeError("title must be text")
        if not isinstance(self.body_text, str):
            raise TypeError("body_text must be text")
        if not isinstance(self.html, str):
            raise TypeError("html must be text")
        if isinstance(self.elapsed_ms, bool) or not isinstance(self.elapsed_ms, int):
            raise TypeError("elapsed_ms must be an integer")
        if self.elapsed_ms < 0:
            raise ValueError("elapsed_ms cannot be negative")


def load_retained_autoevolution_browser_inventory(
    autoevolution_dataset: str | Path,
    fueleconomy_dataset: str | Path,
) -> tuple[tuple[PublicWebSource, ...], dict[str, str]]:
    inventory, versions = load_retained_public_web_inventory(
        autoevolution_dataset,
        fueleconomy_dataset,
    )
    selected = tuple(
        source for source in inventory if source.source_family == AUTOEVOLUTION_FAMILY
    )
    if not selected:
        raise ValueError("retained public-web inventory contains no Autoevolution URLs")
    if len({source.source_url for source in selected}) != len(selected):
        raise ValueError("Autoevolution browser inventory contains duplicate exact URLs")
    return selected, versions


def _sha256_text(value: str) -> tuple[int, str]:
    encoded = value.encode("utf-8")
    return len(encoded), hashlib.sha256(encoded).hexdigest()


def _classify_navigation(
    navigation: BrowserNavigation,
) -> tuple[str, BrowserAcquisitionCode | None, tuple[str, ...], tuple[str, ...]]:
    folded = navigation.body_text.casefold()
    markers = tuple(marker for marker in RELEVANCE_MARKERS if marker in folded)
    block_indicators = tuple(indicator for indicator in BLOCK_INDICATORS if indicator in folded)

    if navigation.http_status < 200 or navigation.http_status >= 300:
        return "FAIL", BrowserAcquisitionCode.HTTP_STATUS, markers, block_indicators
    if not navigation.body_text.strip():
        return "FAIL", BrowserAcquisitionCode.EMPTY_BODY, markers, block_indicators
    if block_indicators:
        return "FAIL", BrowserAcquisitionCode.BLOCK_PAGE, markers, block_indicators
    if len(markers) < MIN_RELEVANCE_MARKERS:
        return "FAIL", BrowserAcquisitionCode.INSUFFICIENT_RELEVANCE, markers, block_indicators
    return "PASS", None, markers, block_indicators


def evaluate_browser_acquisition(
    sources: Iterable[PublicWebSource],
    *,
    navigate: Callable[[str], BrowserNavigation],
    generated_at: datetime | None = None,
    source_dataset_versions: Mapping[str, str] | None = None,
    execution_metadata: Mapping[str, object] | None = None,
) -> dict[str, object]:
    source_list = tuple(sources)
    if not source_list:
        raise ValueError("browser acquisition inventory cannot be empty")
    if any(source.source_family != AUTOEVOLUTION_FAMILY for source in source_list):
        raise ValueError("browser characterization V1 is limited to Autoevolution")
    if len({source.source_url for source in source_list}) != len(source_list):
        raise ValueError("browser acquisition inventory contains duplicate exact URLs")

    timestamp = generated_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware")

    observations: list[dict[str, object]] = []
    failure_codes: Counter[str] = Counter()
    pass_count = 0
    elapsed_total = 0

    for source in source_list:
        base: dict[str, object] = {
            "sourceFamily": source.source_family,
            "sourceUrl": source.source_url,
            "caseIds": list(source.case_ids),
        }
        try:
            navigation = navigate(source.source_url)
        except BrowserAcquisitionError as exc:
            failure_codes[exc.code.value] += 1
            base.update(
                {
                    "status": "FAIL",
                    "code": exc.code.value,
                    "detail": exc.detail,
                }
            )
        else:
            if navigation.source_url != source.source_url:
                raise ValueError("browser navigator returned a result for the wrong source URL")
            status, code, markers, block_indicators = _classify_navigation(navigation)
            body_bytes, body_sha = _sha256_text(navigation.body_text)
            html_bytes, html_sha = _sha256_text(navigation.html)
            elapsed_total += navigation.elapsed_ms
            base.update(
                {
                    "status": status,
                    "code": None if code is None else code.value,
                    "httpStatus": navigation.http_status,
                    "finalUrl": navigation.final_url,
                    "title": navigation.title,
                    "elapsedMs": navigation.elapsed_ms,
                    "bodyUtf8Bytes": body_bytes,
                    "bodySha256": body_sha,
                    "htmlUtf8Bytes": html_bytes,
                    "htmlSha256": html_sha,
                    "relevanceMarkers": list(markers),
                    "blockIndicators": list(block_indicators),
                }
            )
            if code is None:
                pass_count += 1
            else:
                failure_codes[code.value] += 1
        observations.append(base)

    total = len(source_list)
    measured_count = sum(1 for item in observations if "elapsedMs" in item)
    return {
        "schema": REPORT_SCHEMA,
        "inventoryVersion": INVENTORY_VERSION,
        "generatedAt": timestamp.isoformat(),
        "sourceDatasetVersions": dict(sorted((source_dataset_versions or {}).items())),
        "execution": dict(execution_metadata or {}),
        "criteria": {
            "requiredMainDocumentStatus": "2xx",
            "minimumRelevanceMarkerCount": MIN_RELEVANCE_MARKERS,
            "relevanceMarkers": list(RELEVANCE_MARKERS),
            "blockIndicators": list(BLOCK_INDICATORS),
        },
        "metrics": {
            "totalUrlCount": total,
            "representedCaseCount": sum(len(source.case_ids) for source in source_list),
            "passCount": pass_count,
            "failCount": total - pass_count,
            "successRate": pass_count / total,
            "measuredNavigationCount": measured_count,
            "totalNavigationElapsedMs": elapsed_total,
            "meanNavigationElapsedMs": (elapsed_total / measured_count) if measured_count else None,
            "failureCodes": dict(sorted(failure_codes.items())),
        },
        "observations": observations,
    }


__all__ = [
    "AUTOEVOLUTION_FAMILY",
    "BLOCK_INDICATORS",
    "BrowserAcquisitionCode",
    "BrowserAcquisitionError",
    "BrowserNavigation",
    "INVENTORY_VERSION",
    "MIN_RELEVANCE_MARKERS",
    "RELEVANCE_MARKERS",
    "REPORT_SCHEMA",
    "evaluate_browser_acquisition",
    "load_retained_autoevolution_browser_inventory",
]
