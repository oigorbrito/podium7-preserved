from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .domain import AutomotiveIdentity


class MatchOutcome(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class ResolutionDecision:
    outcome: MatchOutcome
    reason: str


def _token(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()
    return " ".join(normalized.split()) or None


def _identity_names(identity: AutomotiveIdentity) -> set[str]:
    names = {_token(identity.model)}
    names.update(_token(alias) for alias in identity.aliases)
    return {name for name in names if name is not None}


def blocking_key(identity: AutomotiveIdentity) -> tuple[str, str] | None:
    make = _token(identity.make)
    model = _token(identity.model)
    if make is None or model is None:
        return None
    return make, model


def generate_candidates(
    target: AutomotiveIdentity,
    candidates: list[tuple[str, AutomotiveIdentity]],
) -> list[tuple[str, AutomotiveIdentity]]:
    target_make = _token(target.make)
    target_names = _identity_names(target)
    if target_make is None or not target_names:
        return []

    result: list[tuple[str, AutomotiveIdentity]] = []
    for candidate_id, candidate in candidates:
        if _token(candidate.make) != target_make:
            continue
        if target_names.intersection(_identity_names(candidate)):
            result.append((candidate_id, candidate))
    return result


def _ranges_overlap(a: AutomotiveIdentity, b: AutomotiveIdentity) -> bool | None:
    if a.year_from is None or a.year_to is None or b.year_from is None or b.year_to is None:
        return None
    return max(a.year_from, b.year_from) <= min(a.year_to, b.year_to)


def resolve_pair(a: AutomotiveIdentity, b: AutomotiveIdentity) -> ResolutionDecision:
    if _token(a.make) != _token(b.make):
        return ResolutionDecision(MatchOutcome.NO_MATCH, "make differs")

    if not _identity_names(a).intersection(_identity_names(b)):
        return ResolutionDecision(MatchOutcome.NO_MATCH, "model/alias differs")

    ids_a = set(a.external_identifiers)
    ids_b = set(b.external_identifiers)
    if ids_a and ids_b and ids_a.intersection(ids_b):
        return ResolutionDecision(MatchOutcome.MATCH, "shared external identifier")

    generation_a = _token(a.generation)
    generation_b = _token(b.generation)
    if generation_a is not None and generation_b is not None and generation_a != generation_b:
        return ResolutionDecision(MatchOutcome.NO_MATCH, "generation differs")

    overlap = _ranges_overlap(a, b)
    if overlap is False:
        return ResolutionDecision(MatchOutcome.NO_MATCH, "year ranges do not overlap")

    powertrain_a = _token(a.powertrain)
    powertrain_b = _token(b.powertrain)
    if powertrain_a is not None and powertrain_b is not None and powertrain_a != powertrain_b:
        return ResolutionDecision(MatchOutcome.NO_MATCH, "powertrain differs")

    if generation_a is not None and generation_a == generation_b:
        if powertrain_a is not None and powertrain_a == powertrain_b:
            return ResolutionDecision(MatchOutcome.MATCH, "same model, generation, and powertrain")

    return ResolutionDecision(MatchOutcome.UNRESOLVED, "insufficient deterministic identity evidence")
