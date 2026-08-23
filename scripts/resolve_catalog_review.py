from __future__ import annotations

import argparse
import json
from pathlib import Path

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import (
    resolve_catalog_review_create,
    resolve_catalog_review_match,
)
from podium7.catalog_review import CatalogReviewQueue


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect and resolve Podium 7 catalog review tasks"
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("podium7.sqlite"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list open review tasks")
    list_parser.add_argument("--limit", type=int, default=100)

    match_parser = subparsers.add_parser(
        "match",
        help="resolve a review by matching an existing catalog vehicle",
    )
    match_parser.add_argument("review_id")
    match_parser.add_argument("vehicle_id")
    match_parser.add_argument("--actor", required=True)
    match_parser.add_argument("--reason", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="resolve a review by creating a new catalog identity",
    )
    create_parser.add_argument("review_id")
    create_parser.add_argument("--actor", required=True)
    create_parser.add_argument("--reason", required=True)

    args = parser.parse_args(argv)

    try:
        with CatalogStore(args.database) as store:
            queue = CatalogReviewQueue(store)
            if args.command == "list":
                _print(
                    {
                        "openCount": queue.count_open(),
                        "items": [
                            task.to_payload()
                            for task in queue.open_tasks(limit=args.limit)
                        ],
                    }
                )
                return 0

            if args.command == "match":
                task = resolve_catalog_review_match(
                    store,
                    args.review_id,
                    args.vehicle_id,
                    actor_id=args.actor,
                    reason=args.reason,
                )
                _print(task.to_payload())
                return 0

            task = resolve_catalog_review_create(
                store,
                args.review_id,
                actor_id=args.actor,
                reason=args.reason,
            )
            _print(task.to_payload())
            return 0
    except (OSError, ValueError) as exc:
        parser.exit(2, f"catalog review failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
