# Review Cause Snapshot V1

Status: implementation prepared; executable validation pending

Issue: #148
Parent: #141
Parent mission: #139

## Purpose

Make the `durable review causes` required by Production Quality Measurement V2 historically auditable. The review queue already persists the raw comparison reasons that caused abstention. Before this block, operational reporting reclassified those reasons at measurement time, so a future classifier change could silently change historical cause counts.

## Contract

Each newly created review task receives one immutable snapshot:

- `review_id` — foreign key to the durable review task;
- `classifier_version` — the exact classifier contract used;
- `causes[]` — the sorted unique cause categories derived only from comparison reasons belonging to the task's candidate vehicles with `MATCH` or `REVIEW` outcomes.

Current classifier version: `catalog-review-cause.v1`.

Raw comparison reasons remain the underlying evidence and are not replaced by the snapshot.

## Fail-closed behavior

- No reason text is invented or normalized beyond the existing `classify_review_reason` contract.
- Multiple distinct causes remain multiple causes; they are not collapsed to a preferred winner.
- Unknown reason text remains `UNKNOWN_REVIEW_CAUSE`.
- A legacy review task without a persisted snapshot is reported as `UNSNAPSHOTTED_LEGACY_REVIEW`; it is not retroactively classified.
- Re-saving an identical snapshot is idempotent. Different content for the same review ID is rejected.

## Transaction boundary

Snapshot creation occurs inside the same outer ingestion transaction as review-task enqueue. A failed snapshot write therefore fails the ingestion transaction rather than leaving a newly created review task with silently missing classification metadata.

## Measurement behavior

`measure_source_backed_operational_corpus` reads persisted snapshots for review-cause counts and reports the classifier versions observed. It still reports the raw persisted review reasons independently.

## Nonchanges

This block does not change:

- resolver or identity semantics;
- evidence thresholds or hierarchy;
- fusion/conflict behavior;
- source policy;
- publication policy;
- review resolution actions.

## Validation

Focused tests cover ingestion-created snapshots, classifier-version retention, multi-cause preservation, idempotency, database reopen persistence, and explicit legacy-unsnapshotted behavior. Repository-required execution remains mandatory before integration and is currently subject to #112.
