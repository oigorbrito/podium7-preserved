from __future__ import annotations

import argparse
import json
from pathlib import Path

from podium7.web_extraction_benchmark import (
    evaluate_web_extraction_bounded_corpus,
    evaluate_web_extraction_bounded_partial_evidence_corpus,
    evaluate_web_extraction_corpus,
    evaluate_web_extraction_partial_evidence_corpus,
    load_web_extraction_bounded_gold,
    load_web_extraction_corpus,
)


DEFAULT_DATASET = Path("benchmarks/web_extraction_source_family_corpus_v1.json")
DEFAULT_BOUNDED_GOLD = Path("benchmarks/web_extraction_bounded_values_v1.json")


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
    parser.add_argument(
        "--partial-evidence",
        action="store_true",
        help="report retained facts plus explicit field issues instead of strict all-or-nothing extraction",
    )
    parser.add_argument(
        "--bounded-values",
        action="store_true",
        help="evaluate the current V2 artifact with source-observed bounded curb-weight semantics",
    )
    parser.add_argument(
        "--bounded-gold",
        type=Path,
        default=DEFAULT_BOUNDED_GOLD,
        help=f"bounded-value gold supplement (default: {DEFAULT_BOUNDED_GOLD})",
    )
    args = parser.parse_args()

    dataset = load_web_extraction_corpus(args.dataset)
    if args.bounded_values:
        bounded_gold = load_web_extraction_bounded_gold(args.bounded_gold, dataset)
        if args.partial_evidence:
            report = evaluate_web_extraction_bounded_partial_evidence_corpus(
                dataset,
                bounded_gold,
            )
        else:
            report = evaluate_web_extraction_bounded_corpus(dataset, bounded_gold)
    elif args.partial_evidence:
        report = evaluate_web_extraction_partial_evidence_corpus(dataset)
    else:
        report = evaluate_web_extraction_corpus(dataset)

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
