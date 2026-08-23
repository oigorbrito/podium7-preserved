from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from podium7.http_acquisition import DirectHttpPolicy
from podium7.public_web_acquisition_benchmark import (
    evaluate_public_web_acquisition,
    load_retained_public_web_inventory,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTOEVOLUTION = ROOT / "benchmarks" / "web_extraction_source_family_corpus_v1.json"
DEFAULT_FUELECONOMY = ROOT / "benchmarks" / "web_extraction_fueleconomy_source_family_v1.json"
DEFAULT_OUTPUT = ROOT / "artifacts" / "public-web-acquisition-report.json"


def _write_json_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
        temporary.replace(path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure direct-HTTP acquisition compatibility against retained public source URLs."
    )
    parser.add_argument("--autoevolution-dataset", type=Path, default=DEFAULT_AUTOEVOLUTION)
    parser.add_argument("--fueleconomy-dataset", type=Path, default=DEFAULT_FUELECONOMY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    parser.add_argument("--max-bytes", type=int, default=2_000_000)
    parser.add_argument("--max-redirects", type=int, default=5)
    args = parser.parse_args()

    inventory, versions = load_retained_public_web_inventory(
        args.autoevolution_dataset,
        args.fueleconomy_dataset,
    )
    policy = DirectHttpPolicy(
        timeout_seconds=args.timeout_seconds,
        max_bytes=args.max_bytes,
        max_redirects=args.max_redirects,
    )
    report = evaluate_public_web_acquisition(
        inventory,
        policy=policy,
        source_dataset_versions=versions,
    )
    _write_json_atomic(args.output, report)
    print(json.dumps(report["metrics"], sort_keys=True))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
