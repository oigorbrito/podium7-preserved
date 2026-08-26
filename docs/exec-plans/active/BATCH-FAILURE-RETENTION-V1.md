# Batch Failure Retention V1

Status: active

Parent: #140
Related: #141
Parent mission: #139

## Outcome
Retain catalog batch ingestion failures durably so failure-rate measurements and diagnosis remain reproducible after the in-memory batch report is gone.

## Boundaries
- persist only failures actually raised while ingesting an already parsed `CatalogBatchEnvelope`;
- a failure snapshot is not evidence and does not authorize catalog publication;
- preserve `recordId`, `evidenceId`, `sourceId`, source/evidence locators, raw-content reference, batch index, error code and message;
- repeated identical failure for an evidence ID is idempotent; conflicting content for the same evidence ID fails closed;
- do not change resolver, review, evidence, source, fusion, publication or retry policy;
- parsing failures that prevent construction of a batch envelope remain outside this store because no valid envelope exists to bind durably.

## Acceptance
Focused tests prove persistence across database reopen, idempotency, conflict rejection, successful records do not create failure snapshots, and operational failure measurement reads the durable store rather than relying only on the returned report.
