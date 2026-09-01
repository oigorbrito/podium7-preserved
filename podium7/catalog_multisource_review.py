from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Sequence

from .catalog import CatalogStore, CatalogVehicleIdentity, ExternalIdentifier
from .catalog_review import (
    CatalogReviewComparison,
    CatalogReviewResolutionAction,
    CatalogReviewState,
)


CATALOG_MULTISOURCE_REVIEW_SCHEMA_VERSION = 1
CATALOG_MULTISOURCE_REVIEW_SCHEMA_COMPONENT = "catalog_multisource_review"


@dataclass(frozen=True)
class CatalogMultisourceReviewTask:
    id: str
    evidence_ids: tuple[str, ...]
    identity: CatalogVehicleIdentity
    candidate_vehicle_ids: tuple[str, ...]
    comparisons: tuple[CatalogReviewComparison, ...]
    field_evidence: tuple[tuple[str, tuple[str, ...]], ...]
    state: CatalogReviewState
    created_at: datetime
    resolution_action: CatalogReviewResolutionAction | None = None
    resolution_vehicle_id: str | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution_reason: str | None = None


def _identity_json(identity: CatalogVehicleIdentity) -> str:
    payload = asdict(identity)
    payload["external_identifiers"] = [
        {"namespace": item.namespace, "value": item.value}
        for item in identity.external_identifiers
    ]
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _identity_from_json(payload: str) -> CatalogVehicleIdentity:
    data = json.loads(payload)
    data["aliases"] = tuple(data.get("aliases", ()))
    data["engine_identifiers"] = tuple(data.get("engine_identifiers", ()))
    data["external_identifiers"] = tuple(
        ExternalIdentifier(**item) for item in data.get("external_identifiers", ())
    )
    return CatalogVehicleIdentity(**data)


def _comparisons_json(comparisons: Sequence[CatalogReviewComparison]) -> str:
    return json.dumps(
        [item.to_payload() for item in comparisons],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _comparisons_from_json(payload: str) -> tuple[CatalogReviewComparison, ...]:
    return tuple(
        CatalogReviewComparison(
            vehicle_id=item["vehicleId"],
            outcome=item["outcome"],
            reason=item["reason"],
        )
        for item in json.loads(payload)
    )


def _field_evidence_json(
    field_evidence: tuple[tuple[str, tuple[str, ...]], ...],
) -> str:
    return json.dumps(
        {field: list(evidence_ids) for field, evidence_ids in field_evidence},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _field_evidence_from_json(
    payload: str,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    data = json.loads(payload)
    return tuple(
        (field, tuple(data[field]))
        for field in sorted(data)
    )


def _field_value(identity: CatalogVehicleIdentity, field_name: str) -> Any:
    value = getattr(identity, field_name)
    if field_name in {"aliases", "engine_identifiers"}:
        return list(value)
    if field_name == "external_identifiers":
        return [
            {"namespace": item.namespace, "value": item.value}
            for item in value
        ]
    return value


def _review_id(evidence_ids: Sequence[str]) -> str:
    material = json.dumps(sorted(evidence_ids), separators=(",", ":"))
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"review_ms_{digest}"


def _require_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


class CatalogMultisourceReviewQueue:
    def __init__(self, store: CatalogStore) -> None:
        self.store = store
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self.store.transaction():
            self.store._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS catalog_v2_multisource_review_tasks (
                    id TEXT PRIMARY KEY,
                    evidence_ids_json TEXT NOT NULL,
                    identity_json TEXT NOT NULL,
                    candidate_vehicle_ids_json TEXT NOT NULL,
                    comparisons_json TEXT NOT NULL,
                    field_evidence_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    resolution_action TEXT,
                    resolution_vehicle_id TEXT,
                    resolved_at TEXT,
                    resolved_by TEXT,
                    resolution_reason TEXT
                );

                CREATE TABLE IF NOT EXISTS catalog_v2_multisource_review_bindings (
                    review_id TEXT NOT NULL REFERENCES catalog_v2_multisource_review_tasks(id),
                    field_name TEXT NOT NULL,
                    field_value_json TEXT NOT NULL,
                    source_id TEXT NOT NULL REFERENCES sources(id),
                    raw_evidence_id TEXT NOT NULL REFERENCES raw_evidence(id),
                    binding_version INTEGER NOT NULL,
                    PRIMARY KEY (review_id, field_name, source_id, raw_evidence_id, field_value_json)
                );
                """
            )
            self.store._connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_catalog_v2_multisource_review_state_created
                ON catalog_v2_multisource_review_tasks(state, created_at, id)
                """
            )
            row = self.store._connection.execute(
                "SELECT version FROM catalog_v2_schema_metadata WHERE component = ?",
                (CATALOG_MULTISOURCE_REVIEW_SCHEMA_COMPONENT,),
            ).fetchone()
            if row is None:
                self.store._connection.execute(
                    "INSERT INTO catalog_v2_schema_metadata(component, version) VALUES (?, ?)",
                    (
                        CATALOG_MULTISOURCE_REVIEW_SCHEMA_COMPONENT,
                        CATALOG_MULTISOURCE_REVIEW_SCHEMA_VERSION,
                    ),
                )
            elif int(row[0]) > CATALOG_MULTISOURCE_REVIEW_SCHEMA_VERSION:
                raise ValueError(
                    f"unsupported catalog multisource review schema version {row[0]}"
                )

    @property
    def schema_version(self) -> int:
        row = self.store._connection.execute(
            "SELECT version FROM catalog_v2_schema_metadata WHERE component = ?",
            (CATALOG_MULTISOURCE_REVIEW_SCHEMA_COMPONENT,),
        ).fetchone()
        return int(row[0])

    def _row_to_task(self, row: Any) -> CatalogMultisourceReviewTask:
        return CatalogMultisourceReviewTask(
            id=row["id"],
            evidence_ids=tuple(json.loads(row["evidence_ids_json"])),
            identity=_identity_from_json(row["identity_json"]),
            candidate_vehicle_ids=tuple(json.loads(row["candidate_vehicle_ids_json"])),
            comparisons=_comparisons_from_json(row["comparisons_json"]),
            field_evidence=_field_evidence_from_json(row["field_evidence_json"]),
            state=CatalogReviewState(row["state"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            resolution_action=(
                None
                if row["resolution_action"] is None
                else CatalogReviewResolutionAction(row["resolution_action"])
            ),
            resolution_vehicle_id=row["resolution_vehicle_id"],
            resolved_at=(
                None
                if row["resolved_at"] is None
                else datetime.fromisoformat(row["resolved_at"])
            ),
            resolved_by=row["resolved_by"],
            resolution_reason=row["resolution_reason"],
        )

    def get(self, review_id: str) -> CatalogMultisourceReviewTask | None:
        row = self.store._connection.execute(
            "SELECT * FROM catalog_v2_multisource_review_tasks WHERE id = ?",
            (review_id,),
        ).fetchone()
        return None if row is None else self._row_to_task(row)

    def review_field_bindings(self, review_id: str) -> list[dict[str, Any]]:
        rows = self.store._connection.execute(
            """
            SELECT field_name, field_value_json, source_id, raw_evidence_id, binding_version
            FROM catalog_v2_multisource_review_bindings
            WHERE review_id = ?
            ORDER BY field_name, source_id, raw_evidence_id, field_value_json
            """,
            (review_id,),
        ).fetchall()
        return [
            {
                "fieldName": row["field_name"],
                "fieldValue": json.loads(row["field_value_json"]),
                "sourceId": row["source_id"],
                "rawEvidenceId": row["raw_evidence_id"],
                "bindingVersion": row["binding_version"],
            }
            for row in rows
        ]

    def enqueue(
        self,
        *,
        evidence_ids: Sequence[str],
        identity: CatalogVehicleIdentity,
        candidate_vehicle_ids: Sequence[str],
        comparisons: Sequence[CatalogReviewComparison],
        field_evidence: tuple[tuple[str, tuple[str, ...]], ...],
        created_at: datetime | None = None,
    ) -> CatalogMultisourceReviewTask:
        normalized_evidence_ids = tuple(sorted(_require_text(value, "evidence_id") for value in evidence_ids))
        if not normalized_evidence_ids:
            raise ValueError("review requires at least one evidence id")
        if len(set(normalized_evidence_ids)) != len(normalized_evidence_ids):
            raise ValueError("review evidence ids must be unique")
        evidence_by_id = {}
        for evidence_id in normalized_evidence_ids:
            evidence = self.store.get_raw_evidence(evidence_id)
            if evidence is None:
                raise ValueError(f"review evidence does not exist: {evidence_id}")
            evidence_by_id[evidence_id] = evidence

        candidate_ids = tuple(candidate_vehicle_ids)
        if not candidate_ids:
            raise ValueError("review requires at least one candidate vehicle")
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("candidate vehicle ids must be unique")
        for vehicle_id in candidate_ids:
            if self.store.get_catalog_vehicle(vehicle_id) is None:
                raise ValueError(f"candidate catalog vehicle does not exist: {vehicle_id}")

        comparison_items = tuple(comparisons)
        comparison_ids = {item.vehicle_id for item in comparison_items}
        missing = [vehicle_id for vehicle_id in candidate_ids if vehicle_id not in comparison_ids]
        if missing:
            raise ValueError("review candidates missing from comparisons: " + ", ".join(missing))

        bound_evidence = {
            evidence_id
            for _, ids in field_evidence
            for evidence_id in ids
        }
        if not bound_evidence.issubset(evidence_by_id):
            raise ValueError("field evidence references evidence outside the review")

        created_at = created_at or datetime.now(timezone.utc)
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")

        review_id = _review_id(normalized_evidence_ids)
        existing = self.get(review_id)
        if existing is not None:
            if (
                existing.evidence_ids == normalized_evidence_ids
                and existing.identity == identity
                and existing.candidate_vehicle_ids == candidate_ids
                and existing.comparisons == comparison_items
                and existing.field_evidence == field_evidence
            ):
                return existing
            raise ValueError("evidence set already has a different multisource review task")

        with self.store.transaction():
            self.store._connection.execute(
                """
                INSERT INTO catalog_v2_multisource_review_tasks(
                    id, evidence_ids_json, identity_json, candidate_vehicle_ids_json,
                    comparisons_json, field_evidence_json, state, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    json.dumps(normalized_evidence_ids, separators=(",", ":")),
                    _identity_json(identity),
                    json.dumps(candidate_ids, ensure_ascii=False, separators=(",", ":")),
                    _comparisons_json(comparison_items),
                    _field_evidence_json(field_evidence),
                    CatalogReviewState.OPEN.value,
                    created_at.isoformat(),
                ),
            )
            for field_name, ids in field_evidence:
                value_json = json.dumps(
                    _field_value(identity, field_name),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                for evidence_id in ids:
                    evidence = evidence_by_id[evidence_id]
                    self.store._insert_once(
                        """
                        INSERT INTO catalog_v2_multisource_review_bindings(
                            review_id, field_name, field_value_json,
                            source_id, raw_evidence_id, binding_version
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            review_id,
                            field_name,
                            value_json,
                            evidence.source_id,
                            evidence_id,
                            1,
                        ),
                    )
        task = self.get(review_id)
        if task is None:
            raise RuntimeError("multisource review task disappeared after enqueue")
        return task

    def resolve(
        self,
        review_id: str,
        *,
        action: CatalogReviewResolutionAction,
        vehicle_id: str,
        actor_id: str,
        reason: str,
        resolved_at: datetime | None = None,
    ) -> CatalogMultisourceReviewTask:
        actor_id = _require_text(actor_id, "actor_id")
        reason = _require_text(reason, "reason")
        vehicle_id = _require_text(vehicle_id, "vehicle_id")
        task = self.get(review_id)
        if task is None:
            raise ValueError("catalog multisource review task does not exist")
        if task.state is CatalogReviewState.RESOLVED:
            if (
                task.resolution_action is action
                and task.resolution_vehicle_id == vehicle_id
                and task.resolved_by == actor_id
                and task.resolution_reason == reason
            ):
                return task
            raise ValueError("catalog multisource review task is already resolved")
        resolved_at = resolved_at or datetime.now(timezone.utc)
        if resolved_at.tzinfo is None or resolved_at.utcoffset() is None:
            raise ValueError("resolved_at must be timezone-aware")
        with self.store.transaction():
            self.store._connection.execute(
                """
                UPDATE catalog_v2_multisource_review_tasks
                SET state = ?, resolution_action = ?, resolution_vehicle_id = ?,
                    resolved_at = ?, resolved_by = ?, resolution_reason = ?
                WHERE id = ? AND state = ?
                """,
                (
                    CatalogReviewState.RESOLVED.value,
                    action.value,
                    vehicle_id,
                    resolved_at.isoformat(),
                    actor_id,
                    reason,
                    review_id,
                    CatalogReviewState.OPEN.value,
                ),
            )
        restored = self.get(review_id)
        if restored is None:
            raise RuntimeError("multisource review task disappeared after resolve")
        return restored


__all__ = [
    "CATALOG_MULTISOURCE_REVIEW_SCHEMA_COMPONENT",
    "CATALOG_MULTISOURCE_REVIEW_SCHEMA_VERSION",
    "CatalogMultisourceReviewQueue",
    "CatalogMultisourceReviewTask",
]
