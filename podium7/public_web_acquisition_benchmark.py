from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlsplit

from .http_acquisition import (
    DirectHttpAcquisition,
    DirectHttpPolicy,
    HttpAcquisitionError,
    acquire_http,
)


REPORT_SCHEMA = "podium7.public-web-acquisition-characterization.v1"
INVENTORY_VERSION = "retained-web-source-urls-1.0"


@dataclass(frozen=True)
class PublicWebSource:
    source_family: str
    source_url: str
    case_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.source_family or self.source_family != self.source_family.strip():
            raise ValueError("source_family must be non-empty normalized text")
        parsed = urlsplit(self.source_url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.fragment:
            raise ValueError(f"public web source must be an exact fragment-free HTTPS URL: {self.source_url!r}")
        if not self.case_ids or any(not value or value != value.strip() for value in self.case_ids):
            raise ValueError("case_ids must contain non-empty identifiers")
        if len(set(self.case_ids)) != len(self.case_ids):
            raise ValueError("case_ids cannot contain duplicates")


def _load_json_object(path: str | Path) -> dict[str, object]:
    raw = Path(path).read_text(encoding="utf-8")

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant {value!r} is not allowed")

    payload = json.loads(raw, parse_constant=reject_constant)
    if not isinstance(payload, dict):
        raise ValueError(f"benchmark root must be an object: {path}")
    return payload


def _cases_from_dataset(path: str | Path) -> tuple[str, list[dict[str, object]]]:
    payload = _load_json_object(path)
    version = payload.get("datasetVersion")
    cases = payload.get("cases")
    if not isinstance(version, str) or not version.strip():
        raise ValueError(f"datasetVersion must be non-empty text: {path}")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"cases must be a non-empty array: {path}")
    normalized: list[dict[str, object]] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case {index} must be an object: {path}")
        case_id = case.get("id")
        source_url = case.get("sourceUrl")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"case {index} id must be non-empty text: {path}")
        if not isinstance(source_url, str) or not source_url.strip():
            raise ValueError(f"case {case_id!r} sourceUrl must be non-empty text: {path}")
        normalized.append(case)
    return version, normalized


def load_retained_public_web_inventory(
    autoevolution_dataset: str | Path,
    fueleconomy_dataset: str | Path,
) -> tuple[tuple[PublicWebSource, ...], dict[str, str]]:
    datasets = (
        ("autoevolution", autoevolution_dataset),
        ("fueleconomy_gov", fueleconomy_dataset),
    )
    versions: dict[str, str] = {}
    grouped: dict[tuple[str, str], list[str]] = {}

    for family, path in datasets:
        version, cases = _cases_from_dataset(path)
        versions[family] = version
        seen_case_ids: set[str] = set()
        for case in cases:
            case_id = str(case["id"])
            source_url = str(case["sourceUrl"])
            if case_id in seen_case_ids:
                raise ValueError(f"duplicate case id {case_id!r} in {family}")
            seen_case_ids.add(case_id)
            key = (family, source_url)
            grouped.setdefault(key, []).append(case_id)

    inventory = tuple(
        PublicWebSource(family, source_url, tuple(case_ids))
        for (family, source_url), case_ids in sorted(grouped.items())
    )
    if len({source.source_url for source in inventory}) != len(inventory):
        families_by_url: dict[str, set[str]] = {}
        for source in inventory:
            families_by_url.setdefault(source.source_url, set()).add(source.source_family)
        overlaps = sorted(url for url, families in families_by_url.items() if len(families) > 1)
        raise ValueError(f"same exact URL appears in multiple source families: {overlaps}")
    return inventory, versions


def _policy_payload(policy: DirectHttpPolicy) -> dict[str, object]:
    return {
        "timeoutSeconds": float(policy.timeout_seconds),
        "maxBytes": policy.max_bytes,
        "maxRedirects": policy.max_redirects,
        "allowedContentTypes": list(policy.allowed_content_types),
        "allowedSchemes": list(policy.allowed_schemes),
        "allowPrivateNetwork": policy.allow_private_network,
        "userAgent": policy.user_agent,
    }


def evaluate_public_web_acquisition(
    sources: Iterable[PublicWebSource],
    *,
    policy: DirectHttpPolicy = DirectHttpPolicy(),
    acquire: Callable[[str, DirectHttpPolicy], DirectHttpAcquisition] = acquire_http,
    generated_at: datetime | None = None,
    source_dataset_versions: dict[str, str] | None = None,
) -> dict[str, object]:
    source_list = tuple(sources)
    if not source_list:
        raise ValueError("public web acquisition inventory cannot be empty")
    if len({source.source_url for source in source_list}) != len(source_list):
        raise ValueError("public web acquisition inventory contains duplicate exact URLs")

    timestamp = generated_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware")

    observations: list[dict[str, object]] = []
    family_totals: Counter[str] = Counter()
    family_passes: Counter[str] = Counter()
    error_codes: Counter[str] = Counter()

    for source in source_list:
        family_totals[source.source_family] += 1
        base: dict[str, object] = {
            "sourceFamily": source.source_family,
            "sourceUrl": source.source_url,
            "caseIds": list(source.case_ids),
        }
        try:
            result = acquire(source.source_url, policy)
        except HttpAcquisitionError as exc:
            error_codes[exc.code.value] += 1
            base.update(
                {
                    "status": "FAIL",
                    "code": exc.code.value,
                    "httpStatus": exc.status,
                    "detail": exc.detail,
                }
            )
        else:
            family_passes[source.source_family] += 1
            base.update(result.to_dict())
        observations.append(base)

    pass_count = sum(family_passes.values())
    total = len(source_list)
    by_family: dict[str, dict[str, object]] = {}
    for family in sorted(family_totals):
        family_total = family_totals[family]
        family_pass = family_passes[family]
        by_family[family] = {
            "totalUrlCount": family_total,
            "passCount": family_pass,
            "failCount": family_total - family_pass,
            "successRate": family_pass / family_total,
        }

    return {
        "schema": REPORT_SCHEMA,
        "inventoryVersion": INVENTORY_VERSION,
        "generatedAt": timestamp.isoformat(),
        "sourceDatasetVersions": dict(sorted((source_dataset_versions or {}).items())),
        "policy": _policy_payload(policy),
        "metrics": {
            "totalUrlCount": total,
            "representedCaseCount": sum(len(source.case_ids) for source in source_list),
            "passCount": pass_count,
            "failCount": total - pass_count,
            "successRate": pass_count / total,
            "bySourceFamily": by_family,
            "failureCodes": dict(sorted(error_codes.items())),
        },
        "observations": observations,
    }


__all__ = [
    "INVENTORY_VERSION",
    "PublicWebSource",
    "REPORT_SCHEMA",
    "evaluate_public_web_acquisition",
    "load_retained_public_web_inventory",
]
