from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re

from .domain import CandidateFact
from .normalization import normalize_fact


@dataclass(frozen=True)
class DocumentExtractionReport:
    sha256: str
    candidates: tuple[CandidateFact, ...]


def _required(text: str, label: str) -> str:
    matches = re.findall(
        rf"^{re.escape(label)}:\s*(.+)$",
        text,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    if not matches:
        raise ValueError(f"required document field {label!r} is missing")
    if len(matches) > 1:
        raise ValueError(f"duplicate document field {label!r}")
    return matches[0].strip()


def extract_ford_dark_horse_document(
    text: str,
    *,
    entity_id: str,
    evidence_id: str,
) -> DocumentExtractionReport:
    _required(text, "MODEL")
    _required(text, "ENGINE")
    power_raw = _required(text, "POWER")
    torque_raw = _required(text, "TORQUE")

    power_match = re.fullmatch(r"([\d.]+)\s*cv", power_raw, flags=re.IGNORECASE)
    torque_match = re.fullmatch(r"([\d.]+)\s*kgfm", torque_raw, flags=re.IGNORECASE)
    if power_match is None or torque_match is None:
        raise ValueError("document values do not satisfy the compiled schema")

    specs = (
        ("power", power_raw, float(power_match.group(1)), "cv"),
        ("torque", torque_raw, float(torque_match.group(1)), "kgfm"),
    )
    candidates: list[CandidateFact] = []
    for attribute, raw, parsed, source_unit in specs:
        normalized = normalize_fact(attribute, parsed, source_unit)
        material = f"{evidence_id}|{attribute}"
        candidate_id = f"candidate:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:24]}"
        candidates.append(
            CandidateFact(
                id=candidate_id,
                entity_candidate_id=entity_id,
                attribute=attribute,
                raw_value=raw,
                normalized_value=normalized.value,
                unit=normalized.unit,
                evidence_id=evidence_id,
                extraction_method="ford-dark-horse-document.v1",
                confidence=None,
                normalization_rule=normalized.rule,
            )
        )

    document_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return DocumentExtractionReport(document_hash, tuple(candidates))
