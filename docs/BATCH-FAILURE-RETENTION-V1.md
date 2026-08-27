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

The in-memory batch report remains the source for failures in the **current execution** (`failed`). The durable store is an immutable historical/audit surface. Its count represents retained failure snapshots in that store and must not be interpreted as the number of currently failing records after later runs.

Durable snapshots can therefore support diagnosis and reproducibility after the original report has been discarded or the database reopened without rewriting execution-local metrics.

## Utility disposition

`BATCH_FAILURE_RETENTION_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

This capability is not redundant with `CatalogBatchReport`: the report is transient, while this store preserves the exact failed envelope identity and diagnostic context across process/database reopen. That enables later audit and root-cause analysis without converting failure data into valid evidence.

Audit hardening added during review:

- persisted payloads are structurally decoded and corrupted/malformed JSON fails closed;
- snapshot/store runtime types are validated explicitly;
- schema metadata must match the supported version;
- store initialization uses Podium's nested transaction mechanism rather than `executescript()+commit`, so constructing the diagnostic store cannot commit an outer ingestion transaction unexpectedly.

If synchronization reveals an equivalent durable failure ledger upstream, classify this block `REDUNDANT`; otherwise current evidence supports integration after executable validation.

## Nonchanges

No resolver, evidence-strength, source, fusion, review, retry or publication rule changes.
