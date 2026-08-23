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
    uses_bounded_parser = False
    for index, item in enumerate(rules_payload):
        if not isinstance(item, dict):
            raise ValueError(f"rule {index} must be an object")
        label = item.get("label")
        attribute = item.get("attribute")
        parser = item.get("parser")
        source_unit = item.get("source_unit")
        label_aliases = item.get("label_aliases", [])
        range_parser = item.get("range_parser")
        if not all(isinstance(value, str) and value.strip() for value in (label, attribute, parser)):
            raise ValueError(f"rule {index} requires label, attribute, and parser")
        if source_unit is not None and (not isinstance(source_unit, str) or not source_unit.strip()):
            raise ValueError(f"rule {index} source_unit must be non-empty string or null")
        if not isinstance(label_aliases, list) or any(
            not isinstance(alias, str) or not alias.strip() for alias in label_aliases
        ):
            raise ValueError(f"rule {index} label_aliases must be a list of non-empty strings")
        if range_parser is not None and (
            not isinstance(range_parser, str) or not range_parser.strip()
        ):
            raise ValueError(f"rule {index} range_parser must be non-empty string or null")

        normalized_label = label.strip()
        normalized_attribute = attribute.strip()
        normalized_source_unit = source_unit.strip() if source_unit is not None else None
        normalized_aliases = tuple(alias.strip() for alias in label_aliases)
        normalized_range_parser = range_parser.strip() if range_parser is not None else None
        attribute_key = normalized_attribute.casefold()
        label_keys = tuple(value.casefold() for value in (normalized_label, *normalized_aliases))

        try:
            compiled = re.compile(parser)
        except re.error as exc:
            raise ValueError(f"rule {index} parser is invalid: {exc}") from exc
        if compiled.groups < 1:
            raise ValueError(f"rule {index} parser must contain a capture group")

        if normalized_range_parser is not None:
            if attribute_key != "curb_weight":
                raise ValueError(
                    f"rule {index} bounded range parsing is unsupported for {normalized_attribute!r}"
                )
            if normalized_source_unit not in {"kg", "lb", "lbs"}:
                raise ValueError(
                    f"rule {index} bounded curb_weight requires kg, lb, or lbs source_unit"
                )
            try:
                compiled_range = re.compile(normalized_range_parser)
            except re.error as exc:
                raise ValueError(f"rule {index} range_parser is invalid: {exc}") from exc
            if compiled_range.groups != 2:
                raise ValueError(f"rule {index} range_parser must contain exactly two capture groups")
            uses_bounded_parser = True

        if attribute_key in seen_attributes:
            raise ValueError(f"duplicate attribute {normalized_attribute!r}")
        if len(set(label_keys)) != len(label_keys):
            raise ValueError(f"rule {index} contains duplicate label aliases")
        duplicate_labels = [
            value for value, key in zip((normalized_label, *normalized_aliases), label_keys) if key in seen_labels
        ]
        if duplicate_labels:
            raise ValueError(f"duplicate label {duplicate_labels[0]!r}")

        seen_attributes.add(attribute_key)
        seen_labels.update(label_keys)
        rules.append(
            WebFieldRule(
                label=normalized_label,
                attribute=normalized_attribute,
                parser=parser,
                source_unit=normalized_source_unit,
                label_aliases=normalized_aliases,
                range_parser=normalized_range_parser,
            )
        )

    return ValidatedExtractionArtifact(
        source_id.strip(),
        tuple(rules),
        artifact_version="v2" if uses_bounded_parser else "v1",
    )
