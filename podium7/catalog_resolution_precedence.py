from __future__ import annotations

from dataclasses import replace

from .catalog import (
    CatalogMatchOutcome,
    CatalogResolutionDecision,
    CatalogVehicleIdentity,
    ExternalIdentifierStrength,
    resolve_catalog_pair,
)
from collections.abc import Mapping


_PARTIAL_LABEL_REVIEW_REASON = "model labels partially overlap"
_NEUTRAL_MODEL_LABEL = "__podium7_partial_label_probe__"


def resolve_catalog_pair_with_structural_precedence(
    a: CatalogVehicleIdentity,
    b: CatalogVehicleIdentity,
    *,
    namespace_registry: Mapping[str, ExternalIdentifierStrength] | None = None,
) -> CatalogResolutionDecision:
    """Let explicit non-label contradictions outrank lexical partial overlap.

    The canonical resolver remains the sole source of contradiction semantics.
    This wrapper only handles its lexical partial-overlap abstention: it removes
    that one uncertainty by giving both observations the same synthetic model
    label and asks the canonical resolver whether the remaining evidence proves
    NO_MATCH. If not, the original REVIEW is preserved unchanged.
    """

    decision = resolve_catalog_pair(
        a,
        b,
        namespace_registry=namespace_registry,
    )
    if (
        decision.outcome is not CatalogMatchOutcome.REVIEW
        or decision.reason != _PARTIAL_LABEL_REVIEW_REASON
    ):
        return decision

    probe_a = replace(a, model=_NEUTRAL_MODEL_LABEL, aliases=())
    probe_b = replace(b, model=_NEUTRAL_MODEL_LABEL, aliases=())
    contradiction_probe = resolve_catalog_pair(
        probe_a,
        probe_b,
        namespace_registry=namespace_registry,
    )
    if contradiction_probe.outcome is CatalogMatchOutcome.NO_MATCH:
        return contradiction_probe
    return decision


__all__ = ["resolve_catalog_pair_with_structural_precedence"]
