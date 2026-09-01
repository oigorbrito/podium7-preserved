from __future__ import annotations

import json
from typing import Sequence

from .catalog import CatalogStore
from .catalog_review import CatalogReviewComparison
from .catalog_review_cause import (
    CatalogReviewCauseSnapshot,
    REVIEW_CAUSE_CLASSIFIER_VERSION,
    classify_review_causes,
)


class CatalogMultisourceReviewCauseStore:
    """Immutable cause snapshots for multi-evidence review tasks."""

    def __init__(self, store: CatalogStore) -> None:
        self.store = store
        with self.store.transaction():
            self.store._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS catalog_v2_multisource_review_cause_snapshots (
                    review_id TEXT PRIMARY KEY REFERENCES catalog_v2_multisource_review_tasks(id),
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
            FROM catalog_v2_multisource_review_cause_snapshots
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
            raise ValueError("multisource review cause snapshot already exists with different content")
        with self.store.transaction():
            self.store._connection.execute(
                """
                INSERT INTO catalog_v2_multisource_review_cause_snapshots(
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
            raise RuntimeError("multisource review cause snapshot disappeared after save")
        return restored


def snapshot_multisource_review_causes(
    store: CatalogStore,
    *,
    review_id: str,
    comparisons: Sequence[CatalogReviewComparison],
    candidate_vehicle_ids: Sequence[str],
    classifier_version: str = REVIEW_CAUSE_CLASSIFIER_VERSION,
    cause_store: CatalogMultisourceReviewCauseStore | None = None,
) -> CatalogReviewCauseSnapshot:
    snapshot = CatalogReviewCauseSnapshot(
        review_id=review_id,
        classifier_version=classifier_version,
        causes=classify_review_causes(comparisons, candidate_vehicle_ids),
    )
    return (cause_store or CatalogMultisourceReviewCauseStore(store)).save(snapshot)


__all__ = [
    "CatalogMultisourceReviewCauseStore",
    "snapshot_multisource_review_causes",
]
