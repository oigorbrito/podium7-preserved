from __future__ import annotations

from dataclasses import dataclass
import json

from .catalog import CatalogStore


BATCH_FAILURE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CatalogBatchFailureSnapshot:
    evidence_id: str
    index: int
    record_id: str | None
    source_id: str
    source_locator: str
    evidence_locator: str
    raw_content_ref: str
    error_code: str
    error_message: str

    def to_payload(self) -> dict[str, object]:
        return {
            "evidenceId": self.evidence_id,
            "index": self.index,
            "recordId": self.record_id,
            "sourceId": self.source_id,
            "sourceLocator": self.source_locator,
            "evidenceLocator": self.evidence_locator,
            "rawContentRef": self.raw_content_ref,
            "error": {"code": self.error_code, "message": self.error_message},
        }


class CatalogBatchFailureStore:
    def __init__(self, store: CatalogStore) -> None:
        self.store = store
        self._initialize()

    def _initialize(self) -> None:
        self.store._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS catalog_batch_failure_metadata (
                component TEXT PRIMARY KEY,
                version INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalog_batch_failures (
                evidence_id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL
            );
            """
        )
        row = self.store._connection.execute(
            "SELECT version FROM catalog_batch_failure_metadata WHERE component = 'catalog-batch-failure'"
        ).fetchone()
        if row is None:
            self.store._connection.execute(
                "INSERT INTO catalog_batch_failure_metadata(component, version) VALUES ('catalog-batch-failure', ?)",
                (BATCH_FAILURE_SCHEMA_VERSION,),
            )
        elif int(row[0]) > BATCH_FAILURE_SCHEMA_VERSION:
            raise ValueError(f"unsupported catalog batch failure schema version {row[0]}")
        self.store._connection.commit()

    @staticmethod
    def _payload(snapshot: CatalogBatchFailureSnapshot) -> str:
        return json.dumps(snapshot.to_payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def save(self, snapshot: CatalogBatchFailureSnapshot) -> None:
        payload = self._payload(snapshot)
        row = self.store._connection.execute(
            "SELECT payload_json FROM catalog_batch_failures WHERE evidence_id = ?",
            (snapshot.evidence_id,),
        ).fetchone()
        if row is None:
            self.store._connection.execute(
                "INSERT INTO catalog_batch_failures(evidence_id, payload_json) VALUES (?, ?)",
                (snapshot.evidence_id, payload),
            )
            return
        if row[0] != payload:
            raise ValueError(
                f"batch failure for evidence {snapshot.evidence_id!r} already exists with different metadata"
            )

    def get(self, evidence_id: str) -> CatalogBatchFailureSnapshot | None:
        row = self.store._connection.execute(
            "SELECT payload_json FROM catalog_batch_failures WHERE evidence_id = ?",
            (evidence_id,),
        ).fetchone()
        if row is None:
            return None
        payload = json.loads(row[0])
        error = payload["error"]
        return CatalogBatchFailureSnapshot(
            evidence_id=payload["evidenceId"],
            index=payload["index"],
            record_id=payload["recordId"],
            source_id=payload["sourceId"],
            source_locator=payload["sourceLocator"],
            evidence_locator=payload["evidenceLocator"],
            raw_content_ref=payload["rawContentRef"],
            error_code=error["code"],
            error_message=error["message"],
        )

    def all(self) -> tuple[CatalogBatchFailureSnapshot, ...]:
        rows = self.store._connection.execute(
            "SELECT evidence_id FROM catalog_batch_failures ORDER BY evidence_id"
        ).fetchall()
        return tuple(self.get(row[0]) for row in rows if self.get(row[0]) is not None)

    def count(self) -> int:
        row = self.store._connection.execute("SELECT COUNT(*) FROM catalog_batch_failures").fetchone()
        return int(row[0])


__all__ = [
    "BATCH_FAILURE_SCHEMA_VERSION",
    "CatalogBatchFailureSnapshot",
    "CatalogBatchFailureStore",
]
