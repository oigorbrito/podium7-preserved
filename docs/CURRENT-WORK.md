# Current work

Status: active

Decision status: `DECISION_REQUIRED = OPERATIONAL_REPLAY_PROVENANCE_MODEL`

Active controlled product-evolution wave:

`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

Authority and measurement/decision record:

- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md)
- [`ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md`](ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md)
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-SINGLE-SOURCE-PATCH-PLAN.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-SINGLE-SOURCE-PATCH-PLAN.md)

## Current measured baseline

Three-dataset wave scope:

- 60 retained record-sides;
- 12 replayable;
- 48 blocked;
- current executed blocker: `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 48`.

No benchmark mutation has been applied by PR #278, so these executed counts remain authoritative until measurements are rerun on a later evidence-mutation change.

## Completed classification work in PR #278

The 48 blocked record-sides are now classified against retained evidence as:

- `COMPOSITE_SUPPORT = 36`;
- `VERIFIED_SINGLE_SOURCE = 10`;
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`.

The classification establishes:

`FIELD_ATTRIBUTION_COMPLETE != OPERATIONAL_REPLAYABLE`

and

`MULTI_SOURCE_EVIDENCE != INVALID_EVIDENCE`

A material majority of blocked observations are validly composite under the retained source contract. The current requirement for one unique source common to every present field is therefore the dominant replay limiter, not only missing attribution metadata.

## Immediate bounded data lane

The 10 verified single-source sides can be explicitly attributed without a replay redesign, but that mutation belongs in a separate evidence-mutation PR after the classification change is authoritative.

Prepared planning expectation after that separate mutation, subject to validation:

- replayable: `12 -> 22`;
- blocked: `48 -> 38`;
- newly replayable via `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- remaining `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2` for the two intentionally unpatched insufficient sides in partially attributed cases.

These are planning expectations, not executed results.

## Decision boundary

`DECISION_REQUIRED = OPERATIONAL_REPLAY_PROVENANCE_MODEL`

Two admissible policies are documented in ADR-0002:

1. `KEEP_UNIQUE_SOURCE_REPLAY`
   - complete only the verified single-source lane;
   - leave valid composite evidence non-replayable by design.

2. `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`
   - introduce a versioned operational provenance contract that preserves per-field evidence from multiple qualified sources;
   - retain conflict handling, source qualification, determinism, traceability and fail-closed behavior.

Do not implement multi-source replay before ADR-0002 is accepted with one policy.

## Validation state

Hosted GitHub Actions resumed repository execution on 2026-09-01.

The first executing run exposed repository harness defects rather than product-test failures:

- new top-level wave documents were missing from `docs/INDEX.md`; corrected in PR #278;
- `CURRENT-WORK.md` used `DECISION_REQUIRED` as the harness status value even though the harness contract permits only `active|none|blocked`; corrected here by keeping `Status: active` and recording the architecture decision separately.

The observed `pdfplumber` import error was downstream of the harness failure because dependency installation was skipped; it is not yet an independent dependency failure.

Require a fresh exact-head run after these corrections before any merge or product-test conclusion.

## Work allowed while decision/validation is pending

- keep PR #278 focused on blocker taxonomy, evidence classification, decision framing and prepared patch plan;
- review the final PR diff for internal consistency;
- use exact-head CI now that hosted runners are executing repository steps;
- once #278 is validated/integrated, create the separate 10-side evidence-mutation change;
- if multi-source replay is selected, implement ADR-0002 in a separate architecture/runtime change with contract-first negative tests.

Current baseline-closeout state remains authoritative in [`PROJECT-STATE.md`](PROJECT-STATE.md) and is not reopened by this controlled product-evolution wave.

Historical integration bookkeeping:

- `PR #272` superseded;
- `PR #274` merged baseline integration anchor;
- `PR #275` and `PR #276` reconciled post-merge documentation authority and volatile-HEAD handling.
