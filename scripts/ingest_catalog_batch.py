from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from podium7.catalog import CatalogStore
from podium7.catalog_batch import ingest_catalog_batch, parse_catalog_batch_payload


def _load_payload(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest an evidence-backed vehicle batch into the Podium 7 Catalog"
    )
    parser.add_argument("input", type=Path, help="JSON object containing a records array")
    parser.add_argument("--database", type=Path, default=Path("podium7.sqlite"))
    args = parser.parse_args(argv)

    try:
        envelopes = parse_catalog_batch_payload(_load_payload(args.input))
        with CatalogStore(args.database) as store:
            report = ingest_catalog_batch(store, envelopes)
        print(json.dumps(report.to_payload(), ensure_ascii=False, indent=2))
        return 0 if report.ok else 3
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "schema": "podium7.catalog-batch-ingestion-report.v1",
                    "ok": False,
                    "error": {
                        "code": "CATALOG_BATCH_INVALID_INPUT",
                        "message": str(exc),
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
