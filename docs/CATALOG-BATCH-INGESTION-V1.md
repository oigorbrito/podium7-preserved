# Catalog Batch Ingestion V1

Status: product workflow.

`Catalog Batch Ingestion V1` extends the single-record catalog ingestion flow so multiple evidence-backed vehicle observations can be processed in one run without weakening the conservative identity policy.

## Input

The CLI accepts one JSON object with a non-empty `records` array. Each record contains:

- optional `recordId` for caller-side traceability;
- `source` with `id`, `name`, and `locator`;
- `evidence` with `id`, `locator`, `retrievedAt`, `acquisitionMethod`, and `rawContentRef`;
- `vehicle` using the existing Catalog Identity V2 field names.

`recordId` values, when present, must be unique inside the batch.

## Execution semantics

Records are processed in input order.

Each record reuses the existing `ingest_catalog_record` workflow, so later records see identities created by earlier records in the same batch.

Each record is an independent persistence unit:

- `CREATED`, `MATCHED`, and `REVIEW` are successful ingestion outcomes;
- `REVIEW` creates the existing durable review task;
- a validation or persistence conflict in one record is reported as a record failure;
- a record failure does not roll back earlier successful records and does not stop later records;
- unexpected internal/runtime failures are not converted into validation failures.

This is deliberate. Batch ingestion is an operational wrapper around the already validated single-record transaction boundary, not a second identity resolver.

## Output

The report schema is:

`podium7.catalog-batch-ingestion-report.v1`

The summary contains:

- `total`
- `succeeded`
- `created`
- `matched`
- `review`
- `failed`

Each record result includes its input index, optional `recordId`, evidence ID, action, canonical vehicle ID when available, durable review ID when applicable, or a stable record-level error object.

A batch is `ok: true` when every record was accepted as `CREATED`, `MATCHED`, or `REVIEW`.

## CLI

```bash
PYTHONPATH=. python scripts/ingest_catalog_batch.py batch.json --database podium7.sqlite
```

Exit codes:

- `0`: every record was accepted;
- `2`: the batch document itself is invalid or unreadable;
- `3`: the batch document was valid, but at least one record failed validation or persistence checks.

## Safety properties

- no resolver-policy change;
- no Catalog JSON Contract V2 change;
- no new automatic merge behavior;
- no global transaction that can erase already accepted evidence because a later independent record is malformed;
- durable review remains the destination for ambiguous identity evidence;
- per-record source/evidence immutability rules remain enforced by the existing ingestion flow.

## Relationship to single-record ingestion

The single-record CLI remains available and unchanged:

```bash
PYTHONPATH=. python scripts/ingest_catalog_record.py record.json --database podium7.sqlite
```

Use batch ingestion when an acquisition adapter or operator already has multiple independent evidence-backed observations ready for reconciliation.
