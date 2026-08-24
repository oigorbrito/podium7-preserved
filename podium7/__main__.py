from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import CatalogStore
from .catalog_ingestion import (
    resolve_catalog_review_create,
    resolve_catalog_review_match,
)
from .catalog_review import CatalogReviewQueue
from .persistence import EvidenceStore, SCHEMA_VERSION


def _health_payload() -> dict[str, object]:
    with EvidenceStore() as store:
        return {
            "status": "PASS",
            "schema_version": store.schema_version,
            "expected_schema_version": SCHEMA_VERSION,
        }


def _require_review_database(database: str) -> Path:
    path = Path(database)
    if database == ":memory:" or not path.is_file():
        raise ValueError("review operator database must be an existing file")
    return path


def _review_payload(args: argparse.Namespace) -> dict[str, object]:
    database = _require_review_database(args.database)
    with CatalogStore(database) as store:
        queue = CatalogReviewQueue(store)
        if args.review_command == "list":
            items = [task.to_payload() for task in queue.open_tasks(limit=args.limit)]
            return {
                "status": "PASS",
                "count": len(items),
                "items": items,
            }

        if args.review_command == "show":
            task = queue.get(args.review_id)
            if task is None:
                raise ValueError("catalog review task does not exist")
            return {"status": "PASS", "item": task.to_payload()}

        if args.review_command == "match":
            task = resolve_catalog_review_match(
                store,
                args.review_id,
                args.vehicle_id,
                actor_id=args.actor,
                reason=args.reason,
            )
            return {"status": "PASS", "item": task.to_payload()}

        if args.review_command == "create":
            task = resolve_catalog_review_create(
                store,
                args.review_id,
                actor_id=args.actor,
                reason=args.reason,
            )
            return {"status": "PASS", "item": task.to_payload()}

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
