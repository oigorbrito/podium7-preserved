from __future__ import annotations

from typing import Any


_DISPOSITIONS = {
    "MISSING_IDENTITY_EVIDENCE": "ENRICH_IDENTITY_EVIDENCE",
    "LABEL_AMBIGUITY": "ENRICH_LABEL_EVIDENCE",
    "IDENTIFIER_CONFLICT": "HUMAN_REVIEW_IDENTIFIER_CONFLICT",
    "MULTIPLE_REVIEW_CAUSES": "HUMAN_REVIEW_MULTIPLE_CAUSES",
}


def prioritize_operational_gaps(measurement: dict[str, Any]) -> list[dict[str, Any]]:
    summary = measurement.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("measurement summary is required")
    total = summary.get("total")
    review = summary.get("review")
    failed = summary.get("failed")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValueError("measurement total must be a positive integer")
    if not isinstance(review, int) or isinstance(review, bool) or review < 0:
        raise ValueError("measurement review must be a non-negative integer")
    if not isinstance(failed, int) or isinstance(failed, bool) or failed < 0:
        raise ValueError("measurement failed must be a non-negative integer")

    priorities: list[dict[str, Any]] = []
    if failed:
        priorities.append(
            {
                "gap": "INGESTION_FAILURES",
                "count": failed,
                "totalShare": failed / total,
                "reviewShare": None,
                "disposition": "FIX_INGESTION_PIPELINE",
            }
        )

    causes = measurement.get("reviewCauses")
    if not isinstance(causes, dict):
        raise ValueError("measurement reviewCauses is required")
    unknown = causes.get("UNKNOWN_REVIEW_CAUSE", 0)
    if not isinstance(unknown, int) or isinstance(unknown, bool) or unknown < 0:
        raise ValueError("unknown review cause count must be a non-negative integer")
    if unknown:
        priorities.append(
            {
                "gap": "UNKNOWN_REVIEW_CAUSE",
                "count": unknown,
                "totalShare": unknown / total,
                "reviewShare": unknown / review if review else None,
                "disposition": "INVESTIGATE_UNKNOWN_REVIEW_CAUSE",
            }
        )

    known: list[tuple[str, int]] = []
    for cause, count in causes.items():
        if cause == "UNKNOWN_REVIEW_CAUSE":
            continue
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError(f"review cause count for {cause!r} must be a non-negative integer")
        if count:
            known.append((cause, count))
    known.sort(key=lambda item: (-item[1], item[0]))
    for cause, count in known:
        priorities.append(
            {
                "gap": cause,
                "count": count,
                "totalShare": count / total,
                "reviewShare": count / review if review else None,
                "disposition": _DISPOSITIONS.get(cause, "INVESTIGATE_UNMAPPED_REVIEW_CAUSE"),
            }
        )
    return priorities


__all__ = ["prioritize_operational_gaps"]
