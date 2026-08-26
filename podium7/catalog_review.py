from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Sequence

from .catalog import CatalogStore, CatalogVehicleIdentity, ExternalIdentifier


CATALOG_REVIEW_SCHEMA_VERSION = 1
CATALOG_REVIEW_SCHEMA_COMPONENT = "catalog_review"


class CatalogReviewState(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class CatalogReviewResolutionAction(str, Enum):
    MATCHED = "MATCHED"
    CREATED = "CREATED"


@dataclass(frozen=True)
class CatalogReviewComparison:
    vehicle_id: str
    outcome: str
    reason: str

    def __post_init__(self) -> None:
        if not self.vehicle_id.strip():
            raise ValueError("comparison vehicle_id is required")
        if self.outcome not in {"MATCH", "NO_MATCH", "REVIEW"}:
            raise ValueError("comparison outcome is invalid")
        if not self.reason.strip():
            raise ValueError("comparison reason is required")

    def to_payload(self) -> dict[str, str]:
        return {
            "vehicleId": self.vehicle_id,
            "outcome": self.outcome,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class CatalogReviewTask:
    id: str
    evidence_id: str
    identity: CatalogVehicleIdentity
    candidate_vehicle_ids: tuple[str, ...]
    comparisons: tuple[CatalogReviewComparison, ...]
    state: CatalogReviewState
    created_at: datetime
    resolution_action: CatalogReviewResolutionAction | None = None
    resolution_vehicle_id: str | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution_reason: str | None = None

    def to_payload(self) -> dict[str, Any]:
        identity = asdict(self.identity)
        identity["aliases"] = list(self.identity.aliases)
        identity["engine_identifiers"] = list(self.identity.engine_identifiers)
        identity["external_identifiers"] = [
            {"namespace": item.namespace, "value": item.value}
            for item in self.identity.external_identifiers
        ]
        return {
            "id": self.id,
            "evidenceId": self.evidence_id,
            "identity": identity,
            "candidateVehicleIds": list(self.candidate_vehicle_ids),
            "comparisons": [item.to_payload() for item in self.comparisons],
            "state": self.state.value,
            "createdAt": self.created_at.isoformat(),
            "resolutionAction": (
                None if self.resolution_action is None else self.resolution_action.value
            ),
            "resolutionVehicleId": self.resolution_vehicle_id,
            "resolvedAt": None if self.resolved_at is None else self.resolved_at.isoformat(),
            "resolvedBy": self.resolved_by,
            "resolutionReason": self.resolution_reason,
        }


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


def _review_id(evidence_id: str) -> str:
    digest = hashlib.sha256(evidence_id.encode("utf-8")).hexdigest()[:24]
    return f"review_{digest}"


def _require_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


class CatalogReviewQueue:
    """Durable review queue for conservative Catalog Identity ingestion decisions."""

    def __init__(self, store: CatalogStore) -> None:
        self.store = store
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        with self.store.transaction():
            self.store._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS catalog_v2_review_tasks (
                    id TEXT PRIMARY KEY,
                    evidence_id TEXT NOT NULL UNIQUE REFERENCES raw_evidence(id),
                    identity_json TEXT NOT NULL,
                    candidate_vehicle_ids_json TEXT NOT NULL,
                    comparisons_json TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    resolution_action TEXT,
                    resolution_vehicle_id TEXT,
                    resolved_at TEXT,
                    resolved_by TEXT,
                    resolution_reason TEXT
                )
                """
            )
            self.store._connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_catalog_v2_review_tasks_state_created
                ON catalog_v2_review_tasks(state, created_at, id)
                """
            )
            row = self.store._connection.execute(
                "SELECT version FROM catalog_v2_schema_metadata WHERE component = ?",
                (CATALOG_REVIEW_SCHEMA_COMPONENT,),
            ).fetchone()
            if row is None:
                self.store._connection.execute(
                    "INSERT INTO catalog_v2_schema_metadata(component, version) VALUES (?, ?)",
                    (CATALOG_REVIEW_SCHEMA_COMPONENT, CATALOG_REVIEW_SCHEMA_VERSION),
                )
            elif int(row[0]) > CATALOG_REVIEW_SCHEMA_VERSION:
                raise ValueError(
                    f"unsupported catalog review schema version {row[0]}"
                )

    @property
    def schema_version(self) -> int:
        row = self.store._connection.execute(
            "SELECT version FROM catalog_v2_schema_metadata WHERE component = ?",
            (CATALOG_REVIEW_SCHEMA_COMPONENT,),
        ).fetchone()
        return int(row[0])

    def _row_to_task(self, row: Any) -> CatalogReviewTask:
        return CatalogReviewTask(
            id=row["id"],
            evidence_id=row["evidence_id"],
            identity=_identity_from_json(row["identity_json"]),
            candidate_vehicle_ids=tuple(json.loads(row["candidate_vehicle_ids_json"])),
            comparisons=_comparisons_from_json(row["comparisons_json"]),
            state=CatalogReviewState(row["state"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            resolution_action=(
                None
                if row["resolution_action"] is None
                else CatalogReviewResolutionAction(row["resolution_action"])
            ),
            resolution_vehicle_id=row["resolution_vehicle_id"],
            resolved_at=(
                None if row["resolved_at"] is None else datetime.fromisoformat(row["resolved_at"])
            ),
            resolved_by=row["resolved_by"],
            resolution_reason=row["resolution_reason"],
        )

    def get(self, review_id: str) -> CatalogReviewTask | None:
        row = self.store._connection.execute(
            "SELECT * FROM catalog_v2_review_tasks WHERE id = ?",
            (review_id,),
        ).fetchone()
        return None if row is None else self._row_to_task(row)

    def get_by_evidence(self, evidence_id: str) -> CatalogReviewTask | None:
        row = self.store._connection.execute(
            "SELECT * FROM catalog_v2_review_tasks WHERE evidence_id = ?",
            (evidence_id,),
        ).fetchone()
        return None if row is None else self._row_to_task(row)

    def enqueue(
        self,
        *,
        evidence_id: str,
        identity: CatalogVehicleIdentity,
        candidate_vehicle_ids: Sequence[str],
        comparisons: Sequence[CatalogReviewComparison],
        created_at: datetime | None = None,
    ) -> CatalogReviewTask:
        evidence_id = _require_text(evidence_id, "evidence_id")
        if self.store.get_raw_evidence(evidence_id) is None:
            raise ValueError("review evidence does not exist")

        candidate_ids = tuple(candidate_vehicle_ids)
        if not candidate_ids:
            raise ValueError("review requires at least one candidate vehicle")
        if any(not isinstance(value, str) or not value.strip() for value in candidate_ids):
            raise ValueError("candidate vehicle ids must be non-empty text")
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("candidate vehicle ids must be unique")
        for vehicle_id in candidate_ids:
            if self.store.get_catalog_vehicle(vehicle_id) is None:
                raise ValueError(f"candidate catalog vehicle does not exist: {vehicle_id}")

        comparison_items = tuple(comparisons)
        if not comparison_items:
            raise ValueError("review comparisons are required")
        comparison_ids = {item.vehicle_id for item in comparison_items}
        missing = [vehicle_id for vehicle_id in candidate_ids if vehicle_id not in comparison_ids]
        if missing:
            raise ValueError(
                "review candidates missing from comparisons: " + ", ".join(missing)
            )

        created_at = created_at or datetime.now(timezone.utc)
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")

        review_id = _review_id(evidence_id)
        existing = self.get_by_evidence(evidence_id)
        if existing is not None:
            if (
                existing.id == review_id
                and existing.identity == identity
                and existing.candidate_vehicle_ids == candidate_ids
                and existing.comparisons == comparison_items
            ):
                return existing
            raise ValueError(
                f"evidence {evidence_id!r} already has a different review task"
            )

        with self.store.transaction():
            self.store._connection.execute(
                """
                INSERT INTO catalog_v2_review_tasks(
                    id, evidence_id, identity_json, candidate_vehicle_ids_json,
                    comparisons_json, state, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    evidence_id,
                    _identity_json(identity),
                    json.dumps(candidate_ids, ensure_ascii=False, separators=(",", ":")),
                    _comparisons_json(comparison_items),
                    CatalogReviewState.OPEN.value,
                    created_at.isoformat(),
                ),
            )
        task = self.get(review_id)
        if task is None:
            raise RuntimeError("review task disappeared after enqueue")
        return task

    def open_tasks(self, *, limit: int = 100) -> list[CatalogReviewTask]:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer")
        rows = self.store._connection.execute(
            """
            SELECT * FROM catalog_v2_review_tasks
            WHERE state = ?
            ORDER BY created_at, id
            LIMIT ?
            """,
            (CatalogReviewState.OPEN.value, limit),
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def count_open(self) -> int:
        row = self.store._connection.execute(
            "SELECT COUNT(*) FROM catalog_v2_review_tasks WHERE state = ?",
            (CatalogReviewState.OPEN.value,),
        ).fetchone()
        return int(row[0])

    def resolve(
        self,
        review_id: str,
        *,
        action: CatalogReviewResolutionAction,
        vehicle_id: str,
        actor_id: str,
        reason: str,
        resolved_at: datetime | None = None,
    ) -> CatalogReviewTask:
        actor_id = _require_text(actor_id, "actor_id")
        reason = _require_text(reason, "reason")
        vehicle_id = _require_text(vehicle_id, "vehicle_id")
        if not isinstance(action, CatalogReviewResolutionAction):
            raise ValueError("action must be a CatalogReviewResolutionAction")

        task = self.get(review_id)
        if task is None:
            raise ValueError("catalog review task does not exist")
        if task.state is CatalogReviewState.RESOLVED:
            if (
                task.resolution_action is action
                and task.resolution_vehicle_id == vehicle_id
                and task.resolved_by == actor_id
                and task.resolution_reason == reason
            ):
                return task
            raise ValueError("catalog review task is already resolved")

        resolved_at = resolved_at or datetime.now(timezone.utc)
        if resolved_at.tzinfo is None or resolved_at.utcoffset() is None:
            raise ValueError("resolved_at must be timezone-aware")

        with self.store.transaction():
            cursor = self.store._connection.execute(
                """
                UPDATE catalog_v2_review_tasks
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
            if cursor.rowcount != 1:
                raise ValueError("catalog review task could not be resolved")
        resolved = self.get(review_id)
        if resolved is None:
            raise RuntimeError("review task disappeared after resolution")
        return resolved


__all__ = [
    "CATALOG_REVIEW_SCHEMA_COMPONENT",
    "CATALOG_REVIEW_SCHEMA_VERSION",
    "CatalogReviewComparison",
    "CatalogReviewQueue",
    "CatalogReviewResolutionAction",
    "CatalogReviewState",
    "CatalogReviewTask",
]
