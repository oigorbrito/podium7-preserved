from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSlice:
    source_family: str
    region: str
    records: int
    independently_inspected: bool = True


def evaluate_source_distribution(slices: tuple[SourceSlice, ...]) -> dict[str, object]:
    if not slices:
        raise ValueError("at least one source slice is required")
    for item in slices:
        if not item.source_family.strip() or not item.region.strip() or item.records <= 0:
            raise ValueError("source family, region and positive record count are required")
        if not item.independently_inspected:
            raise ValueError("uninspected source slices cannot satisfy production distribution")

    by_family = Counter(item.source_family for item in slices)
    by_region = Counter(item.region for item in slices)
    total_records = sum(item.records for item in slices)
    family_records = Counter()
    for item in slices:
        family_records[item.source_family] += item.records
    max_share = max(family_records.values()) / total_records

    # V1 is a bounded distribution gate, not a production-completeness claim.
    # It requires independently inspected evidence across three regions and
    # three source families, while preventing a single family from exceeding
    # 70% of the retained benchmark records.
    passed = len(by_family) >= 3 and len(by_region) >= 3 and max_share <= 0.70
    return {
        "passed": passed,
        "sourceFamilyCount": len(by_family),
        "regionCount": len(by_region),
        "recordCount": total_records,
        "maxSourceFamilyRecordShare": round(max_share, 6),
    }
