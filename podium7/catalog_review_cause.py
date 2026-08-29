from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Sequence

from .catalog import CatalogStore
from .catalog_quality import classify_review_reason
from .catalog_review import CatalogReviewComparison


REVIEW_CAUSE_CLASSIFIER_VERSION = "catalog-review-cause.v1"
LEGACY_UNSNAPSHOTTED_CAUSE = "UNSNAPSHOTTED_LEGACY_REVIEW"


@dataclass(frozen=True)
class CatalogReviewCauseSnapshot:
    review_id: str
    classifier_version: str
    causes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.review_id, str) or not self.review_id.strip():
            raise ValueError("review_id is required")
        if not isinstance(self.classifier_version, str) or not self.classifier_version.strip():
            raise ValueError("classifier_version is required")
        if not isinstance(self.causes, tuple) or not self.causes:
            raise ValueError("at least one review cause is required")
        if any(not isinstance(value, str) or not value.strip() for value in self.causes):
            raise ValueError("review causes must be non-empty text")
        if len(set(self.causes)) != len(self.causes):
            raise ValueError("review causes must be unique")


class CatalogReviewCauseStore:
    """Immutable review-cause snapshots derived from persisted comparison reasons."""

    def __init__(self, store: CatalogStore) -> None:
        self.store = store
        with self.store.transaction():
            self.store._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS catalog_v2_review_cause_snapshots (
                    review_id TEXT PRIMARY KEY REFERENCES catalog_v2_review_tasks(id),
                    classifier_version TEXT NOT NULL,
                    causes_json TEXT NOT NULL
                )
                """
            )

    def get(self, review_id: str) -> CatalogReviewCauseSnapshot | None:
        if not isinstance(review_id, str) or not review_id.strip():
            raise ValueError("review_id is required")
        row = self.store._connection.execute(
            """
            SELECT review_id, classifier_version, causes_json
            FROM catalog_v2_review_cause_snapshots
            WHERE review_id = ?
            """,
            (review_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            raw_causes = json.loads(row["causes_json"])
        except (TypeError, ValueError) as exc:
            raise ValueError("stored review causes must be valid JSON") from exc
        if not isinstance(raw_causes, list):
            raise ValueError("stored review causes must be a JSON array")
        return CatalogReviewCauseSnapshot(
            review_id=row["review_id"],
            classifier_version=row["classifier_version"],
            causes=tuple(raw_causes),
        )

    def save(self, snapshot: CatalogReviewCauseSnapshot) -> CatalogReviewCauseSnapshot:
        if not isinstance(snapshot, CatalogReviewCauseSnapshot):
            raise ValueError("snapshot must be a CatalogReviewCauseSnapshot")
        existing = self.get(snapshot.review_id)
        if existing is not None:
            if existing == snapshot:
                return existing
            raise ValueError("review cause snapshot already exists with different content")

        with self.store.transaction():
            self.store._connection.execute(
                """
                INSERT INTO catalog_v2_review_cause_snapshots(
                    review_id, classifier_version, causes_json
                ) VALUES (?, ?, ?)
                """,
                (
                    snapshot.review_id,
                    snapshot.classifier_version,
                    json.dumps(snapshot.causes, ensure_ascii=False, separators=(",", ":")),
                ),
            )
        restored = self.get(snapshot.review_id)
        if restored is None:
            raise RuntimeError("review cause snapshot disappeared after save")
        return restored


def classify_review_causes(
    comparisons: Sequence[CatalogReviewComparison],
    candidate_vehicle_ids: Sequence[str],
) -> tuple[str, ...]:
    candidates = set(candidate_vehicle_ids)
    reasons = sorted(
        {
            comparison.reason
            for comparison in comparisons
            if comparison.vehicle_id in candidates
            and comparison.outcome in {"MATCH", "REVIEW"}
        }
    )
    if not reasons:
        return ("UNKNOWN_REVIEW_CAUSE",)
    return tuple(sorted({classify_review_reason(reason) for reason in reasons}))


def snapshot_review_causes(
    store: CatalogStore,
    *,
    review_id: str,
    comparisons: Sequence[CatalogReviewComparison],
    candidate_vehicle_ids: Sequence[str],
    classifier_version: str = REVIEW_CAUSE_CLASSIFIER_VERSION,
) -> CatalogReviewCauseSnapshot:
    snapshot = CatalogReviewCauseSnapshot(
        review_id=review_id,
        classifier_version=classifier_version,
        causes=classify_review_causes(comparisons, candidate_vehicle_ids),
    )
    return CatalogReviewCauseStore(store).save(snapshot)


__all__ = [
    "CatalogReviewCauseSnapshot",
    "CatalogReviewCauseStore",
    "LEGACY_UNSNAPSHOTTED_CAUSE",
    "REVIEW_CAUSE_CLASSIFIER_VERSION",
    "classify_review_causes",
    "snapshot_review_causes",
]
