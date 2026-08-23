from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import importlib
import unicodedata
from urllib.parse import urlsplit

from .bound_http_acquisition import acquire_bound_http
from .http_acquisition import DirectHttpAcquisition, DirectHttpPolicy, HttpAcquisitionError, HttpAcquisitionErrorCode

INMETRO_HOST = "www.gov.br"


@dataclass(frozen=True)
class InmetroPbevRecord:
    category: str
    make: str
    model: str
    version: str
    engine: str
    propulsion: str
    fuel: str
    source_url: str
    page_number: int
    row_number: int


def inmetro_pdf_policy() -> DirectHttpPolicy:
    return DirectHttpPolicy(
        max_bytes=2_000_000,
        allowed_content_types=("application/pdf",),
        user_agent="Podium7/0.1 inmetro-pbev-document",
    )


def acquire_inmetro_pbev_pdf(url: str) -> DirectHttpAcquisition:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname is None or parsed.hostname.casefold() != INMETRO_HOST:
        raise HttpAcquisitionError(HttpAcquisitionErrorCode.INVALID_URL, url, "Inmetro PBEV document URL must use https://www.gov.br")
    return acquire_bound_http(url, inmetro_pdf_policy())


def _norm(value: str | None) -> str:
    text = " ".join((value or "").replace("\n", " ").split())
    folded = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in folded if not unicodedata.combining(ch)).casefold()


def _header_map(rows: list[list[str | None]]) -> tuple[int, dict[str, int]] | None:
    aliases = {
        "category": ("categoria",),
        "make": ("marca",),
        "model": ("modelo",),
        "version": ("versao",),
        "engine": ("motor",),
        "propulsion": ("tipo de propulsao", "propulsao"),
        "fuel": ("combustivel",),
    }
    for start in range(min(len(rows), 8)):
        for span in range(1, min(4, len(rows) - start) + 1):
            window = rows[start : start + span]
            width = max((len(row) for row in window), default=0)
            combined: list[str] = []
            for col in range(width):
                combined.append(_norm(" ".join((row[col] or "") for row in window if col < len(row))))
            mapping: dict[str, int] = {}
            for key, candidates in aliases.items():
                for idx, text in enumerate(combined):
                    if any(candidate in text for candidate in candidates):
                        mapping[key] = idx
                        break
            if all(key in mapping for key in aliases):
                return start + span - 1, mapping
    return None


def extract_inmetro_pbev_tables(tables: list[list[list[str | None]]], source_url: str, *, page_number: int = 1) -> tuple[InmetroPbevRecord, ...]:
    records: list[InmetroPbevRecord] = []
    for table in tables:
        header = _header_map(table)
        if header is None:
            continue
        header_end, columns = header
        for row_number, row in enumerate(table[header_end + 1 :], start=header_end + 2):
            def cell(key: str) -> str:
                idx = columns[key]
                return " ".join(((row[idx] if idx < len(row) else None) or "").split())

            make = cell("make")
            model = cell("model")
            if not make or not model:
                continue
            records.append(
                InmetroPbevRecord(
                    category=cell("category"),
                    make=make,
                    model=model,
                    version=cell("version"),
                    engine=cell("engine"),
                    propulsion=cell("propulsion"),
                    fuel=cell("fuel"),
                    source_url=source_url,
                    page_number=page_number,
                    row_number=row_number,
                )
            )
    return tuple(records)


def extract_inmetro_pbev_pdf(pdf_bytes: bytes, source_url: str) -> tuple[InmetroPbevRecord, ...]:
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Inmetro PBEV payload is not a PDF")
    try:
        pdfplumber = importlib.import_module("pdfplumber")
    except ModuleNotFoundError as exc:
        raise RuntimeError("pdfplumber is required for Inmetro PBEV PDF extraction") from exc
    records: list[InmetroPbevRecord] = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as document:
        for page_number, page in enumerate(document.pages, start=1):
            tables = page.extract_tables(
                table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
            )
            records.extend(extract_inmetro_pbev_tables(tables, source_url, page_number=page_number))
    if not records:
        raise ValueError("Inmetro PBEV PDF contained no recognized vehicle table rows")
    return tuple(records)


__all__ = [
    "INMETRO_HOST",
    "InmetroPbevRecord",
    "acquire_inmetro_pbev_pdf",
    "extract_inmetro_pbev_pdf",
    "extract_inmetro_pbev_tables",
    "inmetro_pdf_policy",
]
