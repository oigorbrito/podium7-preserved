# Batch Failure Retention V1

Status: implementation prepared; executable validation pending.

Catalog batch ingestion already reports per-record failures, but those failures previously existed only in the returned in-memory `CatalogBatchReport`. This block makes failures durable and auditable without treating them as valid evidence.

## Contract

For each failure raised while ingesting an already parsed `CatalogBatchEnvelope`, persist an immutable snapshot keyed by `evidenceId` containing:

- batch record index and optional `recordId`;
- `evidenceId` and `sourceId`;
- source and evidence locators;
- raw-content reference;
- error code and message.

A failure snapshot is diagnostic operational data. It does not create `RawEvidence`, candidate facts, canonical facts, review tasks, or publication authority.

Repeated identical snapshots are idempotent. Reusing the same evidence ID with different failure metadata is rejected fail-closed.

Parsing failures that prevent a valid envelope from existing are outside this contract because there is no validated envelope identity to persist.

## Measurement

Failure count for operational reporting can be read from the durable failure store after the original batch report has been discarded or the database reopened.

## Nonchanges

No resolver, evidence-strength, source, fusion, review, retry or publication rule changes.
