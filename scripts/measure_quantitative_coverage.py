from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from podium7.quantitative_coverage import run_coverage_benchmark, summarize_coverage_result


DEFAULT_FIXTURE = ROOT / "benchmarks" / "brazil_quantitative_coverage_v1.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure publication readiness for a retained quantitative coverage fixture."
    )
    parser.add_argument("fixture", nargs="?", default=str(DEFAULT_FIXTURE))
    parser.add_argument("--full", action="store_true", help="include per-field/source/vehicle detail")
    args = parser.parse_args()

    result = run_coverage_benchmark(args.fixture)
    summary = summarize_coverage_result(result)
    if not args.full:
        summary = {
            key: value
            for key, value in summary.items()
            if key not in {"perFieldCoverage", "perSourceCoverage", "perVehicleCoverage"}
        }
    print(json.dumps(summary, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
