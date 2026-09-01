# Current work

Status: active

Decision status: `ACCEPTED = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

Authority:

- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen pre-mutation baseline and evidence classification.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — current executed coverage state after PR #284.
- [`ADR-0002-DECISION-ACCEPTANCE.md`](ADR-0002-DECISION-ACCEPTANCE.md) — accepted Option B decision.
- [`PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md`](PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md) — evaluation specification that seeded the executable v2 contract.

## Current executed state

Active three-dataset scope:

- 60 retained record-sides;
- 22 replayable;
- 38 blocked;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

V3 scope is 72 record-sides: 22 replayable / 50 blocked.

Executed operational effects include 22 replayed records, 7 created, 7 matched, 8 review, 0 failed, and 7 published consumer vehicles.

Residual evidence state:

- `COMPOSITE_SUPPORT = 36` blocked active sides;
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2` blocked active sides;
- no remaining unapplied `VERIFIED_SINGLE_SOURCE` side in the reviewed lane.

The two insufficient sides remain intentionally fail-closed:

- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

## Architecture evidence and decision

PR #282 rejected naive source-specific sequential splitting because publication/review behavior depends on ingestion order.

PR #286 established that existing candidate/evidence persistence can preserve field-level multi-evidence bindings independent of insertion order and roll them back atomically. A replacement persistence subsystem is therefore not the demonstrated blocker.

PR #287 accepted ADR-0002 Option B: `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`.

PR #288 completed the first implementation phase:

- versioned `podium7.catalog-operational.v2` parser/domain layer;
- deterministic source/evidence/field-binding canonicalization;
- stable structured fail-closed errors;
- focused negative contract tests;
- no v1 or runtime ingestion behavior changed.

Established boundaries:

`FIELD_ATTRIBUTION_COMPLETE != OPERATIONAL_REPLAYABLE`

`MULTI_SOURCE_EVIDENCE != INVALID_EVIDENCE`

`PERSISTENCE_CAPABLE != CURRENT_INGESTION_REPRESENTABLE`

## Current implementation gap

`MULTISOURCE_IMPLEMENTATION = PARTIAL`

The remaining gap is runtime ingress/reconciliation and end-to-end field binding:

1. resolve one complete logical v2 identity once, never as sequential source-specific partial records;
2. persist source/evidence objects and CandidateFacts according to explicit `fieldEvidence`;
3. preserve equivalent v1 behavior for single-source records;
4. evolve REVIEW enqueue/identity/idempotency so true per-field evidence survives review;
5. evolve review resolution so CREATE/MATCH attaches CandidateFacts to their actual evidence instead of one task-level evidence;
6. prove CREATE, MATCH, and REVIEW provenance reconstruction and input-order invariance;
7. migrate one representative composite fixture only after those gates pass.

Do not migrate the 36 composite retained sides before the representative runtime path is green.

## Next sequence

1. Add a bounded v2 ingestion/reconciliation path for CREATE and MATCH using the existing resolver and storage primitives.
2. Freeze v1-to-v2 semantic equivalence for single-source observations.
3. Treat REVIEW as a separate schema/API boundary; do not collapse multi-evidence review to one evidence id.
4. Add end-to-end provenance reconstruction tests.
5. Run one representative composite fixture and remeasure replayability/conflicts/publication before broad corpus migration.
6. Reassess `DATA_READY` and `PRODUCT_READY` only after the multi-source implementation lane and representative replay close.

Current baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.