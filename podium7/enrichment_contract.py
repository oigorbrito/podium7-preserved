from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Iterable


CONTRACT_SCHEMA = "podium7.quantitative-enrichment.v1"

# V1 exposes only quantitative fields already represented in retained extraction
# evidence. Expanding this vocabulary is a public-contract change.
CONTRACT_FIELDS = frozenset(
    {
        "displacement",
        "power",
        "torque",
        "length",
        "width",
        "height",
        "wheelbase",
        "curb_weight",
        "fuel_economy_combined",
    }
)
UNIT_REQUIRED_FIELDS = CONTRACT_FIELDS


class KnowledgeState(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class ValueShape(str, Enum):
    SCALAR = "scalar"
    RANGE = "range"
    LIMIT = "limit"
    MULTIPLE = "multiple"


@dataclass(frozen=True)
class EnrichmentContext:
    market: str | None = None
    applicability: str | None = None
    methodology: str | None = None

    def to_payload(self) -> dict[str, str]:
        payload: dict[str, str] = {}
        for key, value in (
            ("market", self.market),
            ("applicability", self.applicability),
            ("methodology", self.methodology),
        ):
            if value is None:
                continue
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"context {key} must be non-empty text when provided")
            payload[key] = value.strip()
        return payload


@dataclass(frozen=True)
class PublishedEnrichmentFact:
    field: str
    knowledge_state: KnowledgeState
    provenance_ref: str
    value_shape: ValueShape | None = None
    value: Any = None
    unit: str | None = None
    context: EnrichmentContext | None = None

    def to_payload(self) -> dict[str, Any]:
        field = _validated_field(self.field)
        if not isinstance(self.knowledge_state, KnowledgeState):
            raise ValueError("knowledge_state must be a KnowledgeState")
        provenance_ref = _validated_text(self.provenance_ref, "provenance_ref")

        if self.knowledge_state is KnowledgeState.KNOWN:
            if not isinstance(self.value_shape, ValueShape):
                raise ValueError("known facts require value_shape")
            if self.value is None:
                raise ValueError("known facts require value")
            _validate_shape(self.value_shape, self.value)
            if self.unit is not None and (not isinstance(self.unit, str) or not self.unit.strip()):
                raise ValueError("unit must be non-empty text when provided")
            if field in UNIT_REQUIRED_FIELDS:
                if self.unit is None:
                    raise ValueError(f"known quantitative field {field!r} requires unit")
                _validate_quantitative_value(self.value_shape, self.value)
        else:
            if self.value_shape is not None or self.value is not None or self.unit is not None:
                raise ValueError("unknown/not_applicable facts cannot carry value, shape, or unit")

        payload: dict[str, Any] = {
            "field": field,
            "knowledgeState": self.knowledge_state.value,
            "provenanceRef": provenance_ref,
        }
        if self.knowledge_state is KnowledgeState.KNOWN:
            payload["valueShape"] = self.value_shape.value
            payload["value"] = self.value
            if self.unit is not None:
                payload["unit"] = self.unit.strip()
        if self.context is not None:
            context_payload = self.context.to_payload()
            if context_payload:
                payload["context"] = context_payload
        _ensure_strict_json(payload)
        return payload


@dataclass(frozen=True)
class PublishedEnrichmentConflict:
    field: str
    provenance_refs: tuple[str, ...]
    reason: str

    def to_payload(self) -> dict[str, Any]:
        field = _validated_field(self.field)
        reason = _validated_text(self.reason, "conflict reason")
        if len(self.provenance_refs) < 2:
            raise ValueError("published conflict requires at least two provenance references")
        refs = tuple(_validated_text(ref, "conflict provenance reference") for ref in self.provenance_refs)
        if len(set(refs)) != len(refs):
            raise ValueError("published conflict provenance references must be unique")
        return {
            "field": field,
            "provenanceRefs": sorted(refs),
            "reason": reason,
        }


def _validated_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def _validated_field(value: str) -> str:
    field = _validated_text(value, "field")
    if field not in CONTRACT_FIELDS:
        raise ValueError(f"unsupported enrichment contract field {field!r}")
    return field


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_quantitative_value(shape: ValueShape, value: Any) -> None:
    if shape is ValueShape.SCALAR and not _is_number(value):
        raise ValueError("quantitative scalar value must be numeric")
    if shape is ValueShape.MULTIPLE:
        if not isinstance(value, list) or any(not _is_number(item) for item in value):
            raise ValueError("quantitative multiple value must be a list of numeric values")


def _validate_shape(shape: ValueShape, value: Any) -> None:
    if shape is ValueShape.SCALAR:
        if isinstance(value, (dict, list, tuple)) or value is None:
            raise ValueError("scalar value must be a JSON scalar")
        return
    if shape is ValueShape.RANGE:
        if not isinstance(value, dict) or set(value) != {"minValue", "maxValue"}:
            raise ValueError("range value must contain exactly minValue and maxValue")
        minimum = value["minValue"]
        maximum = value["maxValue"]
        if not _is_number(minimum) or not _is_number(maximum):
            raise ValueError("range bounds must be numeric")
        if minimum > maximum:
            raise ValueError("range minValue cannot exceed maxValue")
        return
    if shape is ValueShape.LIMIT:
        if not isinstance(value, dict) or set(value) != {"operator", "value"}:
            raise ValueError("limit value must contain exactly operator and value")
        if value["operator"] not in {"lt", "lte", "gt", "gte"}:
            raise ValueError("limit operator is unsupported")
        if not _is_number(value["value"]):
            raise ValueError("limit value must be numeric")
        return
    if shape is ValueShape.MULTIPLE:
        if not isinstance(value, list) or not value:
            raise ValueError("multiple value must be a non-empty list")
        return
    raise ValueError("unsupported value shape")


def _ensure_strict_json(value: Any) -> None:
    try:
        json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("published enrichment values must be strict JSON-compatible") from exc


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _revision(
    vehicle_id: str,
    fact_payloads: list[dict[str, Any]],
    conflict_payloads: list[dict[str, Any]],
) -> str:
    material = {
        "schema": CONTRACT_SCHEMA,
        "vehicleId": vehicle_id,
        "facts": fact_payloads,
        "conflicts": conflict_payloads,
    }
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def publish_enrichment_payload(
    vehicle_id: str,
    facts: Iterable[PublishedEnrichmentFact],
    conflicts: Iterable[PublishedEnrichmentConflict] = (),
) -> dict[str, Any]:
    canonical_vehicle_id = _validated_text(vehicle_id, "vehicle_id")

    fact_payloads = [fact.to_payload() for fact in facts]
    fact_payloads.sort(key=lambda item: (item["field"], item["provenanceRef"], _canonical_json(item)))
    conflict_payloads = [conflict.to_payload() for conflict in conflicts]
    conflict_payloads.sort(key=lambda item: (item["field"], _canonical_json(item)))

    fact_fields = [item["field"] for item in fact_payloads]
    duplicates = sorted({field for field in fact_fields if fact_fields.count(field) > 1})
    if duplicates:
        raise ValueError("published enrichment cannot contain duplicate fields: " + ", ".join(duplicates))

    conflict_fields = [item["field"] for item in conflict_payloads]
    duplicate_conflicts = sorted({field for field in conflict_fields if conflict_fields.count(field) > 1})
    if duplicate_conflicts:
        raise ValueError("published enrichment cannot contain duplicate conflicts: " + ", ".join(duplicate_conflicts))

    overlap = sorted(set(fact_fields).intersection(conflict_fields))
    if overlap:
        raise ValueError("unresolved conflict blocks canonical publication for fields: " + ", ".join(overlap))

    return {
        "schema": CONTRACT_SCHEMA,
        "vehicleId": canonical_vehicle_id,
        "revision": _revision(canonical_vehicle_id, fact_payloads, conflict_payloads),
        "facts": fact_payloads,
        "conflicts": conflict_payloads,
    }


def publish_enrichment_json(
    vehicle_id: str,
    facts: Iterable[PublishedEnrichmentFact],
    conflicts: Iterable[PublishedEnrichmentConflict] = (),
    *,
    indent: int | None = 2,
) -> str:
    return json.dumps(
        publish_enrichment_payload(vehicle_id, facts, conflicts),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        indent=indent,
    )


__all__ = [
    "CONTRACT_FIELDS",
    "CONTRACT_SCHEMA",
    "EnrichmentContext",
    "KnowledgeState",
    "PublishedEnrichmentConflict",
    "PublishedEnrichmentFact",
    "UNIT_REQUIRED_FIELDS",
    "ValueShape",
    "publish_enrichment_json",
    "publish_enrichment_payload",
]
