from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from typing import Any

from .domain import AutomotiveIdentity, CanonicalFact, Conflict


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def export_entity_payload(
    entity_id: str,
    identity: AutomotiveIdentity,
    canonical_facts: list[CanonicalFact],
    conflicts: list[Conflict],
) -> dict[str, Any]:
    facts = sorted(canonical_facts, key=lambda fact: (fact.attribute, fact.id))
    unresolved = sorted(conflicts, key=lambda conflict: (conflict.attribute, conflict.id))
    return {
        "entity": {"id": entity_id, **_jsonable(identity)},
        "canonicalFacts": [_jsonable(fact) for fact in facts],
        "conflicts": [_jsonable(conflict) for conflict in unresolved],
        "quality": {
            "canonicalFactCount": len(facts),
            "conflictCount": len(unresolved),
            "hasUnresolvedConflicts": any(
                conflict.resolution_state.value != "RESOLVED" for conflict in unresolved
            ),
        },
    }


def export_entity_json(
    entity_id: str,
    identity: AutomotiveIdentity,
    canonical_facts: list[CanonicalFact],
    conflicts: list[Conflict],
    *,
    indent: int | None = 2,
) -> str:
    return json.dumps(
        export_entity_payload(entity_id, identity, canonical_facts, conflicts),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        indent=indent,
    )


def write_entity_json(
    path: str | Path,
    entity_id: str,
    identity: AutomotiveIdentity,
    canonical_facts: list[CanonicalFact],
    conflicts: list[Conflict],
) -> Path:
    destination = Path(path)
    destination.write_text(
        export_entity_json(entity_id, identity, canonical_facts, conflicts) + "\n",
        encoding="utf-8",
    )
    return destination
