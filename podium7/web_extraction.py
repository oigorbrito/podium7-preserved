from __future__ import annotations

from dataclasses import dataclass
import re

from .normalization import normalize_bounded_fact, normalize_fact


@dataclass(frozen=True)
class WebFieldRule:
    label: str
    attribute: str
    parser: str
    source_unit: str | None
    label_aliases: tuple[str, ...] = ()
    range_parser: str | None = None


@dataclass(frozen=True)
class ExtractedWebFact:
    attribute: str
    raw_value: str
    parsed_value: object
    normalized_value: object
    unit: str | None
    extraction_rule: str
    normalization_rule: str
    source_label: str


@dataclass(frozen=True)
class WebExtractionIssue:
    attribute: str
    label: str
    code: str
    message: str
    raw_value: str | None = None


@dataclass(frozen=True)
class WebExtractionReport:
    facts: tuple[ExtractedWebFact, ...]
    issues: tuple[WebExtractionIssue, ...]


AUTOEVOLUTION_ARTEGA_GT_RULES_V1: tuple[WebFieldRule, ...] = (
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
    WebFieldRule(
        "Combined",
        "fuel_economy_combined",
        r"^.*?\(([\d.]+)\s*L/100Km\)",
        "L/100km",
        ("Combined (EPA)",),
    ),
)


AUTOEVOLUTION_ARTEGA_GT_RULES_V2: tuple[WebFieldRule, ...] = tuple(
    WebFieldRule(
        label=rule.label,
        attribute=rule.attribute,
        parser=rule.parser,
        source_unit=rule.source_unit,
        label_aliases=rule.label_aliases,
        range_parser=(
            r"^.*?\((\d+)\s*-\s*(\d+)\s*kg\)"
            if rule.attribute == "curb_weight"
            else None
        ),
    )
    for rule in AUTOEVOLUTION_ARTEGA_GT_RULES_V1
)

# Current reusable artifact. V1 remains named above so historical benchmark
# evidence can be replayed without silently applying newer parsing semantics.
AUTOEVOLUTION_ARTEGA_GT_RULES = AUTOEVOLUTION_ARTEGA_GT_RULES_V2


# Second source-family artifact. The MPG parser is deliberately anchored so
# MPGe cannot be silently interpreted as gasoline MPG. A PHEV gas-only label
# is an explicit alias because it carries the same gasoline-MPG semantics.
FUELECONOMY_GOV_VEHICLE_RULES_V1: tuple[WebFieldRule, ...] = (
    WebFieldRule(
        "Combined MPG",
        "fuel_economy_combined",
        r"^(\d+(?:\.\d+)?)\s*MPG$",
        "mpg-US",
        ("Combined MPG on Gas Only",),
    ),
    WebFieldRule("Drive", "drivetrain", r"^(.+)$", None),
    WebFieldRule("Fuel Type", "fuel_type", r"^(.+)$", None),
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


def _parse_values(text: str) -> dict[str, tuple[str, str]]:
    values: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        if ": | " not in line:
            continue
        label, raw = line.split(": | ", 1)
        normalized_label = label.strip()
        key = normalized_label.casefold()
        if key in values:
            raise ValueError(f"duplicate web field {normalized_label!r}")
        values[key] = (normalized_label, raw.strip())
    return values


def _rule_namespace(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", value):
        raise ValueError("rule_namespace must be a lowercase source-family token")
    return value


def _bounded_fact(
    rule: WebFieldRule,
    source_label: str,
    raw: str,
    match: re.Match[str],
    *,
    rule_namespace: str,
) -> tuple[ExtractedWebFact | None, WebExtractionIssue | None]:
    minimum = _coerce(match.group(1))
    maximum = _coerce(match.group(2))
    parsed = {"minValue": minimum, "maxValue": maximum}
    try:
        normalized = normalize_bounded_fact(
            rule.attribute,
            minimum,
            maximum,
            rule.source_unit,
        )
    except ValueError as exc:
        message = f"bounded rule {rule.label!r} rejected acquired value {raw!r}: {exc}"
        return None, WebExtractionIssue(
            attribute=rule.attribute,
            label=source_label,
            code="INVALID_BOUNDED_VALUE",
            message=message,
            raw_value=raw,
        )

    return (
        ExtractedWebFact(
            attribute=rule.attribute,
            raw_value=raw,
            parsed_value=parsed,
            normalized_value=normalized.value,
            unit=normalized.unit,
            extraction_rule=f"{rule_namespace}.{rule.attribute}.bounded.v2",
            normalization_rule=normalized.rule,
            source_label=source_label,
        ),
        None,
    )


def extract_with_rules_report(
    text: str,
    rules: tuple[WebFieldRule, ...],
    *,
    rule_namespace: str = "autoevolution",
) -> WebExtractionReport:
    namespace = _rule_namespace(rule_namespace)
    values = _parse_values(text)
    extracted: list[ExtractedWebFact] = []
    issues: list[WebExtractionIssue] = []

    for rule in rules:
        candidate_labels = (rule.label, *rule.label_aliases)
        matches = [values[label.casefold()] for label in candidate_labels if label.casefold() in values]

        if not matches:
            message = f"required web field {rule.label!r} is missing"
            issues.append(
                WebExtractionIssue(
                    attribute=rule.attribute,
                    label=rule.label,
                    code="MISSING_FIELD",
                    message=message,
                )
            )
            continue

        if len(matches) > 1:
            matched_labels = ", ".join(repr(label) for label, _ in matches)
            message = f"multiple web labels matched rule {rule.label!r}: {matched_labels}"
            issues.append(
                WebExtractionIssue(
                    attribute=rule.attribute,
                    label=rule.label,
                    code="AMBIGUOUS_LABEL",
                    message=message,
                )
            )
            continue

        source_label, raw = matches[0]
        match = re.search(rule.parser, raw, flags=re.IGNORECASE)
        if match is not None:
            parsed = _coerce(match.group(1))
            normalized = normalize_fact(rule.attribute, parsed, rule.source_unit)
            extracted.append(
                ExtractedWebFact(
                    attribute=rule.attribute,
                    raw_value=raw,
                    parsed_value=parsed,
                    normalized_value=normalized.value,
                    unit=normalized.unit,
                    extraction_rule=f"{namespace}.{rule.attribute}.v1",
                    normalization_rule=normalized.rule,
                    source_label=source_label,
                )
            )
            continue

        if rule.range_parser is not None:
            range_match = re.search(rule.range_parser, raw, flags=re.IGNORECASE)
            if range_match is not None:
                fact, issue = _bounded_fact(
                    rule,
                    source_label,
                    raw,
                    range_match,
                    rule_namespace=namespace,
                )
                if issue is not None:
                    issues.append(issue)
                elif fact is not None:
                    extracted.append(fact)
                continue

        message = f"rule {rule.label!r} did not match acquired value {raw!r}"
        issues.append(
            WebExtractionIssue(
                attribute=rule.attribute,
                label=source_label,
                code="PARSER_MISMATCH",
                message=message,
                raw_value=raw,
            )
        )

    return WebExtractionReport(tuple(extracted), tuple(issues))


def extract_with_rules(
    text: str,
    rules: tuple[WebFieldRule, ...],
    *,
    rule_namespace: str = "autoevolution",
) -> list[ExtractedWebFact]:
    report = extract_with_rules_report(text, rules, rule_namespace=rule_namespace)
    if report.issues:
        raise ValueError(report.issues[0].message)
    return list(report.facts)


def extract_autoevolution_artega_gt(text: str) -> list[ExtractedWebFact]:
    return extract_with_rules(text, AUTOEVOLUTION_ARTEGA_GT_RULES)


def extract_fueleconomy_gov_vehicle(text: str) -> list[ExtractedWebFact]:
    return extract_with_rules(
        text,
        FUELECONOMY_GOV_VEHICLE_RULES_V1,
        rule_namespace="fueleconomy_gov",
    )
