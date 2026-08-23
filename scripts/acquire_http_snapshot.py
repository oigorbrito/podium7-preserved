from __future__ import annotations

import argparse
import json

from podium7.http_acquisition import (
    DirectHttpPolicy,
    HttpAcquisitionError,
    acquire_and_freeze_http,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Acquire one explicit HTTPS locator and freeze the validated byte response as a local snapshot."
    )
    parser.add_argument("url", help="exact HTTPS source locator")
    parser.add_argument("snapshot", help="destination snapshot path")
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    parser.add_argument("--max-bytes", type=int, default=2_000_000)
    parser.add_argument("--max-redirects", type=int, default=5)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = DirectHttpPolicy(
            timeout_seconds=args.timeout_seconds,
            max_bytes=args.max_bytes,
            max_redirects=args.max_redirects,
        )
        result = acquire_and_freeze_http(
            args.url,
            args.snapshot,
            policy,
            overwrite=args.overwrite,
        )
    except (HttpAcquisitionError, ValueError) as exc:
        if isinstance(exc, HttpAcquisitionError):
            payload = exc.to_dict()
        else:
            payload = {
                "status": "FAIL",
                "code": "INVALID_POLICY",
                "detail": str(exc),
            }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
