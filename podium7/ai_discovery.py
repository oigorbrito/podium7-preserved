from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .web_extraction import WebFieldRule


@dataclass(frozen=True)
class ValidatedExtractionArtifact:
    source_id: str
    rules: tuple[WebFieldRule, ...]
    artifact_version: str = "v1"


def validate_extraction_artifact(payload: dict[str, Any]) -> ValidatedExtractionArtifact:
    source_id = payload.get("source_id")
    rules_payload = payload.get("rules")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id is required")
    if not isinstance(rules_payload, list) or not rules_payload:
        raise ValueError("at least one extraction rule is required")

    rules: list[WebFieldRule] = []
    seen_attributes: set[str] = set()
    seen_labels: set[str] = set()
    for index, item in enumerate(rules_payload):
        if not isinstance(item, dict):
            raise ValueError(f"rule {index} must be an object")
        label = item.get("label")
        attribute = item.get("attribute")
        parser = item.get("parser")
        source_unit = item.get("source_unit")
        if not all(isinstance(value, str) and value.strip() for value in (label, attribute, parser)):
            raise ValueError(f"rule {index} requires label, attribute, and parser")
        if source_unit is not None and (not isinstance(source_unit, str) or not source_unit.strip()):
            raise ValueError(f"rule {index} source_unit must be non-empty string or null")

        normalized_label = label.strip()
        normalized_attribute = attribute.strip()
        label_key = normalized_label.casefold()
        attribute_key = normalized_attribute.casefold()

        try:
            compiled = re.compile(parser)
        except re.error as exc:
            raise ValueError(f"rule {index} parser is invalid: {exc}") from exc
        if compiled.groups < 1:
            raise ValueError(f"rule {index} parser must contain a capture group")
        if attribute_key in seen_attributes:
            raise ValueError(f"duplicate attribute {normalized_attribute!r}")
        if label_key in seen_labels:
            raise ValueError(f"duplicate label {normalized_label!r}")
        seen_attributes.add(attribute_key)
        seen_labels.add(label_key)
        rules.append(
            WebFieldRule(
                normalized_label,
                normalized_attribute,
                parser,
                source_unit.strip() if source_unit is not None else None,
            )
        )

    return ValidatedExtractionArtifact(source_id.strip(), tuple(rules))
