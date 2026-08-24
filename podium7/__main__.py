from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

from .catalog import CATALOG_SCHEMA_VERSION, CatalogStore, export_catalog_vehicle_payload
from .catalog_ingestion import (
    resolve_catalog_review_create,
    resolve_catalog_review_match,
)
from .catalog_review import (
    CATALOG_REVIEW_SCHEMA_COMPONENT,
    CATALOG_REVIEW_SCHEMA_VERSION,
    CatalogReviewQueue,
    CatalogReviewTask,
)
from .persistence import EvidenceStore, SCHEMA_VERSION


REVIEW_REQUIRED_TABLES = {
    "sources",
    "automotive_entities",
    "raw_evidence",
    "candidate_facts",
    "provenance",
    "canonical_facts",
    "conflicts",
    "catalog_v2_schema_metadata",
    "catalog_v2_vehicles",
    "catalog_v2_identity_revisions",
    "catalog_v2_redirects",
    "catalog_v2_physical_listings",
    "catalog_v2_candidate_facts",
    "catalog_v2_provenance",
    "catalog_v2_canonical_facts",
    "catalog_v2_conflicts",
    "catalog_v2_review_tasks",
}
REVIEW_REQUIRED_INDEXES = {
    "idx_evidence_source",
    "idx_candidate_entity",
    "idx_candidate_evidence",
    "idx_canonical_entity",
    "idx_catalog_v2_review_tasks_state_created",
}


def _health_payload() -> dict[str, object]:
    with EvidenceStore() as store:
        return {
            "status": "PASS",
            "schema_version": store.schema_version,
            "expected_schema_version": SCHEMA_VERSION,
        }


def _require_review_database(database: str) -> Path:
    path = Path(database)
    error = "review operator database must be an existing file with a Podium catalog review schema"
    if database == ":memory:" or not path.is_file():
        raise ValueError(error)

    try:
        uri = path.resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            schema_objects = connection.execute(
                "SELECT type, name FROM sqlite_master WHERE type IN ('table', 'index')"
            ).fetchall()
            tables = {name for object_type, name in schema_objects if object_type == "table"}
            indexes = {name for object_type, name in schema_objects if object_type == "index"}
            if (
                user_version != SCHEMA_VERSION
                or not REVIEW_REQUIRED_TABLES.issubset(tables)
                or not REVIEW_REQUIRED_INDEXES.issubset(indexes)
            ):
                raise ValueError(error)
            versions = dict(
                connection.execute(
                    "SELECT component, version FROM catalog_v2_schema_metadata "
                    "WHERE component IN (?, ?)",
                    ("catalog", CATALOG_REVIEW_SCHEMA_COMPONENT),
                )
            )
    except sqlite3.Error as exc:
        raise ValueError(error) from exc

    if versions != {
        "catalog": CATALOG_SCHEMA_VERSION,
        CATALOG_REVIEW_SCHEMA_COMPONENT: CATALOG_REVIEW_SCHEMA_VERSION,
    }:
        raise ValueError(error)
    return path


def _review_evidence_payload(store: CatalogStore, task: CatalogReviewTask) -> dict[str, object]:
    evidence = store.get_raw_evidence(task.evidence_id)
    if evidence is None:
        raise RuntimeError("catalog review evidence does not exist")
    source = store.get_source(evidence.source_id)
    if source is None:
        raise RuntimeError("catalog review source does not exist")
    return {
        "id": evidence.id,
        "sourceId": evidence.source_id,
        "locator": evidence.locator,
        "retrievedAt": evidence.retrieved_at.isoformat(),
        "acquisitionMethod": evidence.acquisition_method,
        "rawContentRef": evidence.raw_content_ref,
        "source": {
            "id": source.id,
            "name": source.name,
            "locator": source.locator,
        },
    }


def _review_task_payload(
    store: CatalogStore,
    task: CatalogReviewTask,
    *,
    include_context: bool = False,
) -> dict[str, object]:
    payload = task.to_payload()
    if include_context:
        payload["candidateEntities"] = [
            export_catalog_vehicle_payload(store, vehicle_id)["entity"]
            for vehicle_id in task.candidate_vehicle_ids
        ]
        payload["evidence"] = _review_evidence_payload(store, task)
    return payload


def _review_payload(args: argparse.Namespace) -> dict[str, object]:
    database = _require_review_database(args.database)
    with CatalogStore(database) as store:
        queue = CatalogReviewQueue(store)
        if args.review_command == "list":
            items = [
                _review_task_payload(store, task)
                for task in queue.open_tasks(limit=args.limit)
            ]
            return {
                "status": "PASS",
                "count": len(items),
                "items": items,
            }

        if args.review_command == "show":
            task = queue.get(args.review_id)
            if task is None:
                raise ValueError("catalog review task does not exist")
            return {
                "status": "PASS",
                "item": _review_task_payload(store, task, include_context=True),
            }

        if args.review_command == "match":
            task = resolve_catalog_review_match(
                store,
                args.review_id,
                args.vehicle_id,
                actor_id=args.actor,
                reason=args.reason,
            )
            return {"status": "PASS", "item": _review_task_payload(store, task)}

        if args.review_command == "create":
            task = resolve_catalog_review_create(
                store,
                args.review_id,
                actor_id=args.actor,
                reason=args.reason,
            )
            return {"status": "PASS", "item": _review_task_payload(store, task)}

    raise ValueError("unsupported catalog review command")


def _add_review_commands(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    review = subparsers.add_parser("review", help="operate the durable catalog review queue")
    review_subparsers = review.add_subparsers(dest="review_command", required=True)

    list_parser = review_subparsers.add_parser("list", help="list open catalog reviews")
    list_parser.add_argument("--database", required=True, help="existing catalog SQLite database")
    list_parser.add_argument("--limit", type=int, default=100)

    show_parser = review_subparsers.add_parser("show", help="show one catalog review")
    show_parser.add_argument("review_id")
    show_parser.add_argument("--database", required=True, help="existing catalog SQLite database")

    match_parser = review_subparsers.add_parser("match", help="resolve a review to an existing candidate")
    match_parser.add_argument("review_id")
    match_parser.add_argument("vehicle_id")
    match_parser.add_argument("--database", required=True, help="existing catalog SQLite database")
    match_parser.add_argument("--actor", required=True)
    match_parser.add_argument("--reason", required=True)

    create_parser = review_subparsers.add_parser("create", help="resolve a review by creating a new catalog identity")
    create_parser.add_argument("review_id")
    create_parser.add_argument("--database", required=True, help="existing catalog SQLite database")
    create_parser.add_argument("--actor", required=True)
    create_parser.add_argument("--reason", required=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m podium7")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="check runtime and persistence readiness")
    _add_review_commands(subparsers)
    args = parser.parse_args(argv)

    try:
        if args.command == "health":
            payload = _health_payload()
        elif args.command == "review":
            payload = _review_payload(args)
        else:
            return 2
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1

    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
