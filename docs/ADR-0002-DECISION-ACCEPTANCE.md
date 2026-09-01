# ADR-0002 decision acceptance — field-level multi-source replay

Status: `ACCEPTED`

Date: 2026-09-01

Parent decision record: `ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md`

Accepted policy: `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

## Decision

Podium 7 will evolve operational replay to preserve qualified provenance at field granularity when one logical vehicle observation is supported by multiple evidence sources.

The accepted direction is ADR-0002 Option B. This acceptance resolves the product-architecture choice only; it does not by itself authorize broad corpus migration or bypass implementation gates.

The existing v1 single-source path remains supported during a versioned migration.

## Evidence supporting the decision

Wave 01 established the post-attribution retained-scope boundary:

- 60 active record-sides;
- 22 replayable after applying the 10 verified single-source mappings;
- 38 blocked;
- 36 `COMPOSITE_SUPPORT`;
- 2 `INSUFFICIENT_SINGLE_SOURCE_SUPPORT`.

PR #282 executed the source-split experiment and established:

- `SOURCE_SPLIT_ORDER_DEPENDENT = YES`;
- `SECOND_OBSERVATION_FIELD_CANDIDATES_ATTACHED = NO`;
- `SOURCE_EVIDENCE_PRESERVED = YES`;
- `NAIVE_PRE_INGESTION_SOURCE_SPLIT = REJECTED_BY_EVIDENCE`.

Therefore sequentially splitting a composite observation into ordinary v1 observations is not an admissible implementation shortcut.

PR #286 executed the atomic multi-evidence storage experiment and established:

- multiple evidence objects can bind disjoint fields on one logical catalog identity;
- field-to-evidence and evidence-to-source bindings are invariant to source insertion order;
- multi-evidence writes roll back atomically on failure;
- all executable validation steps passed; the workflow-level failure was limited to validation-artifact upload after the test suite completed.

Therefore there is no evidence that the persisted `CandidateFact` / evidence storage model must be replaced for Option B. The dominant implementation gap is the operational ingress/reconciliation/field-binding path.

## Accepted implementation boundary

Implementation should proceed contract-first around a versioned v2 operational envelope with:

- `sources[]`;
- `evidence[]`;
- explicit `fieldEvidence` for every present vehicle field;
- deterministic canonicalization independent of input ordering;
- CREATE, MATCH, and REVIEW paths that preserve field-to-evidence bindings end to end.

The evaluation draft `PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md` is the starting contract specification. Its semantics remain subject to implementation tests; acceptance of Option B does not mean every draft serialization detail is immutable.

## Non-negotiable invariants

- no synthetic aggregate source;
- no heuristic source selection;
- field-complete provenance for every present field;
- source qualification remains enforced per attributed field;
- conflicts remain conflicts/review evidence;
- equivalent inputs are deterministic regardless of source/evidence ordering;
- malformed, incomplete, unknown, or inconsistent provenance fails closed;
- repeated evidence references do not create false corroboration;
- v1 single-source compatibility is preserved during migration;
- field-level provenance remains reconstructable after CREATE, MATCH, and REVIEW;
- field-attribution completeness and operational replayability remain separate metrics.

## Rejected implementation shortcut

`NAIVE_PRE_INGESTION_SOURCE_SPLIT` is rejected by executed evidence from #282 and must not be used as the multi-source implementation.

## Implementation sequence

1. Promote the v2 contract from evaluation draft to implementation contract with stable structural error codes and canonicalization rules.
2. Implement parser/domain validation and negative tests before changing runtime ingestion behavior.
3. Add a multi-evidence ingestion/reconciliation path that reuses existing persistence primitives where their invariants already hold.
4. Preserve field/source/evidence bindings through CREATE, MATCH, and REVIEW.
5. Freeze v1-to-v2 semantic-equivalence tests for single-source records.
6. Migrate one representative composite fixture and remeasure replayability, conflicts, publication behavior, and provenance reconstruction.
7. Expand to the 36 composite retained sides only after the representative path is green.

## Explicitly not authorized by this decision

- weakening source qualification;
- inferring missing field provenance;
- selecting a preferred source heuristically;
- creating synthetic provenance;
- suppressing conflicts;
- changing identity thresholds for coverage gain;
- flag-day removal of the v1 contract;
- broad benchmark migration before implementation gates pass.

## Decision state

`ADR_0002 = ACCEPTED`

`ADR_0002_DECISION = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

`MULTISOURCE_IMPLEMENTATION = NOT_YET_COMPLETE`

`CURRENT_IMPLEMENTATION_GAP = VERSIONED_INGRESS_RECONCILIATION_AND_FIELD_BINDING`
