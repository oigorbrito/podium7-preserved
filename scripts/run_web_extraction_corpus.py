from __future__ import annotations

import argparse
import json
from pathlib import Path

from podium7.web_extraction_benchmark import (
    evaluate_web_extraction_corpus,
    load_web_extraction_corpus,
)


DEFAULT_DATASET = Path("benchmarks/web_extraction_source_family_corpus_v1.json")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the frozen Autoevolution source-family extraction corpus."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"corpus dataset (default: {DEFAULT_DATASET})",
    )
    args = parser.parse_args()

    dataset = load_web_extraction_corpus(args.dataset)
    report = evaluate_web_extraction_corpus(dataset)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
