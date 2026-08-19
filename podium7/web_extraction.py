from __future__ import annotations

from dataclasses import dataclass
import re

from .normalization import normalize_fact


@dataclass(frozen=True)
class WebFieldRule:
    label: str
    attribute: str
    parser: str
    source_unit: str | None


@dataclass(frozen=True)
class ExtractedWebFact:
    attribute: str
    raw_value: str
    parsed_value: object
    normalized_value: object
    unit: str | None
    extraction_rule: str
    normalization_rule: str


AUTOEVOLUTION_ARTEGA_GT_RULES: tuple[WebFieldRule, ...] = (
    WebFieldRule("Displacement", "displacement", r"^(\d+)\s*cm3", "cc"),
    WebFieldRule("Power", "power", r"^[\d.]+\s*KW.*?/\s*(\d+)\s*HP", "hp"),
    WebFieldRule("Torque", "torque", r"^.*?/\s*(\d+)\s*Nm", "Nm"),
    WebFieldRule("Fuel", "fuel_type", r"^(.+)$", None),
    WebFieldRule("Drive Type", "drivetrain", r"^(.+)$", None),
    WebFieldRule("Gearbox", "transmission", r"^(.+)$", None),
    WebFieldRule("Length", "length", r"^.*?\((\d+)\s*mm\)", "mm"),
    WebFieldRule("Width", "width", r"^.*?\((\d+)\s*mm\)", "mm"),
    WebFieldRule("Height", "height", r"^.*?\((\d+)\s*mm\)", "mm"),
    WebFieldRule("Wheelbase", "wheelbase", r"^.*?\((\d+)\s*mm\)", "mm"),
    WebFieldRule("Unladen Weight", "curb_weight", r"^.*?\((\d+)\s*kg\)", "kg"),
    WebFieldRule("Combined", "fuel_economy_combined", r"^.*?\(([\d.]+)\s*L/100Km\)", "L/100km"),
)


def _coerce(value: str) -> object:
    stripped = value.strip()
    try:
        return int(stripped)
    except ValueError:
        try:
            return float(stripped)
        except ValueError:
            return stripped


def extract_with_rules(text: str, rules: tuple[WebFieldRule, ...]) -> list[ExtractedWebFact]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ": | " not in line:
            continue
        label, raw = line.split(": | ", 1)
        key = label.strip().casefold()
        if key in values:
            raise ValueError(f"duplicate web field {label.strip()!r}")
        values[key] = raw.strip()

    extracted: list[ExtractedWebFact] = []
    for rule in rules:
        raw = values.get(rule.label.casefold())
        if raw is None:
            raise ValueError(f"required web field {rule.label!r} is missing")
        match = re.search(rule.parser, raw, flags=re.IGNORECASE)
        if match is None:
            raise ValueError(f"rule {rule.label!r} did not match acquired value {raw!r}")
        parsed = _coerce(match.group(1))
        normalized = normalize_fact(rule.attribute, parsed, rule.source_unit)
        extracted.append(
            ExtractedWebFact(
                attribute=rule.attribute,
                raw_value=raw,
                parsed_value=parsed,
                normalized_value=normalized.value,
                unit=normalized.unit,
                extraction_rule=f"autoevolution.{rule.attribute}.v1",
                normalization_rule=normalized.rule,
            )
        )
    return extracted


def extract_autoevolution_artega_gt(text: str) -> list[ExtractedWebFact]:
    return extract_with_rules(text, AUTOEVOLUTION_ARTEGA_GT_RULES)
