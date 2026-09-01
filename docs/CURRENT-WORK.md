# Current work

Status: active

Decision status: `DECISION_REQUIRED = OPERATIONAL_REPLAY_PROVENANCE_MODEL`

Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

Authority:

- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md)
- [`ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md`](ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md)
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-SINGLE-SOURCE-PATCH-PLAN.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-SINGLE-SOURCE-PATCH-PLAN.md)

## Measured baseline

- 60 retained record-sides;
- 12 replayable;
- 48 blocked;
- executed blocker: `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 48`.

No benchmark mutation is included in PR #278. These counts remain authoritative until a later evidence-mutation run changes them.

## Retained-evidence classification

- `COMPOSITE_SUPPORT = 36`;
- `VERIFIED_SINGLE_SOURCE = 10`;
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`.

Established boundaries:

`FIELD_ATTRIBUTION_COMPLETE != OPERATIONAL_REPLAYABLE`

`MULTI_SOURCE_EVIDENCE != INVALID_EVIDENCE`

The unique-common-source replay contract is the dominant limiter for the 36 valid composite sides.

## Bounded single-source lane

The exact 10-side field-attribution plan is prepared but unapplied.

Planning target if all ten mappings validate under the unchanged replay contract:

- replayable `12 -> 22`;
- blocked `48 -> 38`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

These are planning expectations, not executed results.

## Architecture decision

ADR-0002 leaves two admissible policies open:

1. `KEEP_UNIQUE_SOURCE_REPLAY` — complete only the verified single-source lane.
2. `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY` — version the operational provenance contract and preserve field-level multi-source evidence.

Do not implement multi-source runtime behavior before the ADR selects a policy.

Current code inspection shows Option B can likely reuse existing candidate/provenance/review storage; the main gap is the one-source/one-evidence ingestion and review API.

## Validation

Hosted Actions resumed repository execution on 2026-09-01.

Executed harness defects found and corrected in PR #278:

- new top-level docs were missing from `docs/INDEX.md`;
- `CURRENT-WORK` status must be one of `active|none|blocked`;
- this file must stay at or below 100 lines.

The earlier `pdfplumber` import error occurred only after harness failure skipped dependency installation, so it is not yet an independent failure.

Require fresh exact-head CI before merge or product-test conclusions.

## Next sequence

1. Validate and integrate #278 only when exact-head gates are green.
2. Apply the prepared 10-side attribution plan in a separate evidence-mutation PR and measure actual blocker transitions.
3. Keep the two insufficient sides blocked unless stronger qualified evidence appears.
4. Keep the 36 composite sides unchanged until ADR-0002 selects a replay policy.
5. If Option B is selected, implement it separately with contract-first negative tests and v1 equivalence tests.

Current baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative and is not reopened by this wave.
