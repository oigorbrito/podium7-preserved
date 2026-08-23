from __future__ import annotations

import json
from pathlib import Path

from podium7.web_acquisition import evaluate_current_web_acquisition


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    report = evaluate_current_web_acquisition(ROOT)
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
