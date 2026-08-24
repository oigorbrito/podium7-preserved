from __future__ import annotations

from typing import Any

from .operational_priority import prioritize_operational_gaps


_ALLOWED_ACTIONS = {
    "ENRICH_IDENTITY_EVIDENCE": "Acquire missing model-year, trim-defining, or other deterministic identity evidence before reconsidering the review.",
    "ENRICH_LABEL_EVIDENCE": "Acquire source-backed canonical model/alias evidence before reconsidering the review.",
    "HUMAN_REVIEW_IDENTIFIER_CONFLICT": "Keep the record in durable human review until stronger source-backed identity evidence resolves the identifier conflict.",
    "HUMAN_REVIEW_MULTIPLE_CAUSES": "Keep the record in durable human review and resolve each measured ambiguity with additional evidence.",
}


def plan_measured_operational_dispositions(measurement: dict[str, Any]) -> dict[str, Any]:
    priorities = prioritize_operational_gaps(measurement)
    actions: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for item in priorities:
        disposition = item["disposition"]
        instruction = _ALLOWED_ACTIONS.get(disposition)
        if instruction is None:
            unresolved.append(dict(item))
            continue
        actions.append(
            {
                "gap": item["gap"],
                "count": item["count"],
                "disposition": disposition,
                "instruction": instruction,
                "resolverPolicyChange": False,
            }
        )

    assigned = sum(action["count"] for action in actions)
    return {
        "schema": "podium7.measured-operational-disposition.v1",
        "actions": actions,
        "unresolvedPriorities": unresolved,
        "assignedReviewTasks": assigned,
        "resolverPolicyChanges": 0,
    }


__all__ = ["plan_measured_operational_dispositions"]
