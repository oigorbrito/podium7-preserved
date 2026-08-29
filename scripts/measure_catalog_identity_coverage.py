from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from podium7.catalog_coverage import measure_published_catalog_identity_coverage


DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure consumer-visible catalog identity-field coverage."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for deterministic JSON output; stdout is used when omitted.",
    )
    args = parser.parse_args()

    report = measure_published_catalog_identity_coverage(DATASETS)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
