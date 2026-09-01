# Current work

Status: active

Decision status: `DECISION_REQUIRED = OPERATIONAL_REPLAY_PROVENANCE_MODEL`

Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

Authority:

- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen pre-mutation baseline and evidence classification.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — current executed coverage state after PR #284.
- [`ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md`](ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md).
- [`PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md`](PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md) — evaluation-only Option B contract.

## Current executed state

Active three-dataset scope:

- 60 retained record-sides;
- 22 replayable;
- 38 blocked;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

The bounded single-source attribution lane is complete and integrated by PR #284. Exact-head CI passed the complete isolated suite on Python 3.11 and Python 3.13.

V3 scope is 72 record-sides: 22 replayable / 50 blocked.

Executed operational effects include 22 replayed records, 7 created, 7 matched, 8 review, 0 failed, and 7 published consumer vehicles.

## Residual evidence state

- `COMPOSITE_SUPPORT = 36` blocked active sides;
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2` blocked active sides;
- no remaining unapplied `VERIFIED_SINGLE_SOURCE` side in the reviewed lane.

The two insufficient sides remain intentionally fail-closed:

- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

Established boundaries:

`FIELD_ATTRIBUTION_COMPLETE != OPERATIONAL_REPLAYABLE`

`MULTI_SOURCE_EVIDENCE != INVALID_EVIDENCE`

`FIELD_ATTRIBUTION_COMPLETE != CURRENT_INGESTION_REPRESENTABLE`

## Architecture decision

ADR-0002 remains undecided. The dominant remaining limiter is the operational replay provenance model for the 36 valid composite sides, not missing single-source metadata.

PR #282 executed and rejected naive source-specific sequential splitting because publication/review behavior depends on ingestion order.

The evaluation-only multi-evidence v2 contract documents an admissible fail-closed design surface but does not authorize implementation.

Do not implement multi-source runtime behavior before ADR-0002 selects a policy.

## Next sequence

1. Preserve the integrated 22/38 state and the two insufficient fail-closed sides.
2. Compare admissible multi-source designs against provenance fidelity, order independence, conflict behavior, v1 equivalence, source qualification, review semantics, and fail-closed rejection.
3. Select ADR-0002 only from executed/static evidence; do not choose by preference.
4. Implement the selected policy separately with exact contract and regression gates.
5. Reassess `DATA_READY` and `PRODUCT_READY` only after the architecture lane closes; do not infer product readiness from 22/60 alone.

Current baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.