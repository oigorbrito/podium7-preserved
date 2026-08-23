from __future__ import annotations

import argparse
import json
from pathlib import Path

from podium7.fueleconomy_web_benchmark import (
    evaluate_fueleconomy_corpus,
    load_fueleconomy_corpus,
)


DEFAULT_CORPUS = Path("benchmarks/web_extraction_fueleconomy_source_family_v1.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the frozen FuelEconomy.gov web corpus")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--partial-evidence", action="store_true")
    args = parser.parse_args()

    corpus = load_fueleconomy_corpus(args.corpus)
    report = evaluate_fueleconomy_corpus(corpus, partial_evidence=args.partial_evidence)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
