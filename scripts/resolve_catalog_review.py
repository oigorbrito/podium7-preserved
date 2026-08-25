from __future__ import annotations

import argparse
from pathlib import Path

from podium7.__main__ import main as podium_main


def _translate_args(args: argparse.Namespace) -> list[str]:
    translated = ["review", args.command]
    if args.command in {"show", "match", "create"}:
        translated.append(args.review_id)
    if args.command == "match":
        translated.append(args.vehicle_id)
    translated.extend(["--database", str(args.database)])
    if args.command == "list":
        translated.extend(["--limit", str(args.limit)])
    if args.command in {"match", "create"}:
        translated.extend(["--actor", args.actor, "--reason", args.reason])
    return translated


def main(argv: list[str] | None = None) -> int:
    """Compatibility entry point for the canonical catalog review operator.

    New automation should use ``python -m podium7 review ...`` directly. This
    wrapper intentionally contains no database-opening or resolution logic so
    the legacy command cannot bypass the canonical existing-database preflight
    or mutation/audit rules.
    """

    parser = argparse.ArgumentParser(
        description="Compatibility wrapper for the Podium 7 catalog review operator"
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("podium7.sqlite"),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="list open review tasks")
    list_parser.add_argument("--limit", type=int, default=100)

    show_parser = subparsers.add_parser("show", help="show one review task")
    show_parser.add_argument("review_id")

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
    return podium_main(_translate_args(args))


if __name__ == "__main__":
    raise SystemExit(main())
