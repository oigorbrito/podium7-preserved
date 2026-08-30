from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from urllib.parse import urlsplit

from .bound_http_acquisition import acquire_bound_http
from .http_acquisition import (
    DirectHttpAcquisition,
    DirectHttpPolicy,
    FrozenHttpSnapshot,
    HttpAcquisitionError,
    HttpAcquisitionErrorCode,
    freeze_http_snapshot,
)


PDF_MEDIA_TYPE = "application/pdf"


@dataclass(frozen=True)
class PdfAcquisitionContract:
    source_id: str
    locator: str
    max_bytes: int = 4_000_000
    timeout_seconds: float = 15.0
    user_agent: str = "Podium7/0.1 bounded-pdf-acquisition"

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("source_id must be non-empty text")
        if not isinstance(self.locator, str) or not self.locator.strip() or self.locator != self.locator.strip():
            raise ValueError("locator must be non-empty text without surrounding whitespace")
        parsed = urlsplit(self.locator)
        if parsed.scheme.casefold() != "https" or not parsed.hostname:
            raise ValueError("PDF locator must be an absolute HTTPS URL")
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise ValueError("PDF locator cannot contain credentials or fragments")
        if isinstance(self.max_bytes, bool) or not isinstance(self.max_bytes, int) or self.max_bytes < 1:
            raise ValueError("max_bytes must be a positive integer")
        if isinstance(self.timeout_seconds, bool) or not isinstance(self.timeout_seconds, (int, float)):
            raise ValueError("timeout_seconds must be a finite positive number")
        if not math.isfinite(float(self.timeout_seconds)) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a finite positive number")
        if not isinstance(self.user_agent, str) or not self.user_agent.strip():
            raise ValueError("user_agent must be non-empty text")


def pdf_http_policy(contract: PdfAcquisitionContract) -> DirectHttpPolicy:
    if not isinstance(contract, PdfAcquisitionContract):
        raise ValueError("contract must be PdfAcquisitionContract")
    return DirectHttpPolicy(
        timeout_seconds=contract.timeout_seconds,
        max_bytes=contract.max_bytes,
        max_redirects=0,
        allowed_content_types=(PDF_MEDIA_TYPE,),
        allowed_schemes=("https",),
        allow_private_network=False,
        user_agent=contract.user_agent,
    )


def acquire_pdf(contract: PdfAcquisitionContract) -> DirectHttpAcquisition:
    policy = pdf_http_policy(contract)
    acquisition = acquire_bound_http(contract.locator, policy)
    if acquisition.requested_url != contract.locator or acquisition.final_url != contract.locator:
        raise HttpAcquisitionError(
            HttpAcquisitionErrorCode.INVALID_URL,
            acquisition.final_url,
            "bounded PDF acquisition requires exact requested and final locator identity",
        )
    if acquisition.content_type != PDF_MEDIA_TYPE:
        raise HttpAcquisitionError(
            HttpAcquisitionErrorCode.UNSUPPORTED_CONTENT_TYPE,
            acquisition.final_url,
            f"expected {PDF_MEDIA_TYPE!r}, observed {acquisition.content_type!r}",
            status=acquisition.status,
        )
    return acquisition


def acquire_and_freeze_pdf(
    contract: PdfAcquisitionContract,
    destination: str | Path,
    *,
    overwrite: bool = False,
) -> FrozenHttpSnapshot:
    acquisition = acquire_pdf(contract)
    return freeze_http_snapshot(acquisition, destination, overwrite=overwrite)


__all__ = [
    "PDF_MEDIA_TYPE",
    "PdfAcquisitionContract",
    "acquire_and_freeze_pdf",
    "acquire_pdf",
    "pdf_http_policy",
]
