from __future__ import annotations

import argparse
import json
import sys

from .persistence import EvidenceStore, SCHEMA_VERSION


def _health_payload() -> dict[str, object]:
    with EvidenceStore() as store:
        return {
            "status": "PASS",
            "schema_version": store.schema_version,
            "expected_schema_version": SCHEMA_VERSION,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m podium7")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health", help="check runtime and persistence readiness")
    args = parser.parse_args(argv)

    if args.command == "health":
        try:
            payload = _health_payload()
        except Exception as exc:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
            return 1
        print(json.dumps(payload, sort_keys=True))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
