from __future__ import annotations

import argparse
import json
from pathlib import Path

from podium7.catalog_benchmark import (
    evaluate_catalog_identity_benchmark,
    load_catalog_identity_benchmark,
)


DEFAULT_DATASET = (
    Path(__file__).resolve().parents[1]
    / "benchmarks"
    / "catalog_identity_golden_v1.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Podium 7 catalog identity golden benchmark")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    args = parser.parse_args()

    dataset = load_catalog_identity_benchmark(args.dataset)
    report = evaluate_catalog_identity_benchmark(dataset)
    print(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
