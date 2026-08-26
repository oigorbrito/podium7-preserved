# Exec Plan — Review Cause Snapshot V1

Issue: #148
Parent: #141

## Outcome

Persist the review-cause classification used when a review task is created so production-quality measurement can report historically stable causes without reclassifying old tasks.

## Steps

1. Reuse the existing `CatalogReviewTask` raw comparison reasons as the evidence surface.
2. Add a separate immutable snapshot store keyed by review ID.
3. Version the classifier contract and preserve multiple/unknown causes explicitly.
4. Write the snapshot in the same ingestion transaction as review-task enqueue.
5. Change operational measurement to consume snapshots and expose unsnapshotted legacy tasks explicitly.
6. Add focused persistence/idempotency/multi-cause tests.
7. Update durable documentation and index.
8. Run repository-required validation; do not merge without executable green CI.

## Boundaries

No resolver, evidence, ambiguity, fusion, publication, source-policy or review-resolution behavior changes. No historical task is backfilled by inference.
