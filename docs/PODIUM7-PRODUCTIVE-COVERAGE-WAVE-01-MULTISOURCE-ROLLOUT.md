# PODIUM7 Productive Coverage Wave 01 — multisource rollout state

Status: active / executed through Corolla Cross family rollout

Date: 2026-09-01

Authority scope: executed post-ADR-0002 operational multi-source coverage state. This document supersedes the post-single-source count as the current Wave 01 execution snapshot; the frozen pre-mutation classification remains in `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`.

## Decision and runtime status

Accepted architecture decision:

`PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

The runtime lane is no longer partial:

- v2 operational provenance contract/parser is implemented;
- CREATE and MATCH preserve field-level multi-evidence bindings;
- v1-to-v2 single-source semantic equivalence is covered;
- REVIEW has a dedicated multi-evidence path rather than collapsing to one evidence id;
- review-cause snapshots preserve multi-source evidence context;
- CandidateFact -> evidence -> source reconstruction is tested;
- the retained representative composite probe passed before evidence rollout.

The remaining work is evidence-qualified corpus rollout, not basic runtime representability.

## Executed active-scope measurement

Three retained Wave 01 datasets remain the measurement denominator:

- `catalog_identity_golden_v1.json`;
- `catalog_identity_golden_br_v1.json`;
- `catalog_identity_br_adjacent_incomplete_v1.json`.

After the verified single-source lane and the Corolla Cross multi-source rollout:

- retained record-sides: `60`;
- replayable: `28`;
- blocked: `32`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 6`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 30`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

The six v2 record-sides are exactly the retained Corolla Cross composite family in `catalog_identity_golden_br_v1.json`:

1. `br-match-corolla-cross-xrx-hybrid-my25:left`;
2. `br-match-corolla-cross-xrx-hybrid-my25:right`;
3. `br-no-match-corolla-cross-xrx-hybrid-vs-xrx-flex:left`;
4. `br-no-match-corolla-cross-xrx-hybrid-vs-xrx-flex:right`;
5. `br-review-corolla-cross-xrx-hybrid-missing-variant:left`;
6. `br-review-corolla-cross-xrx-hybrid-missing-variant:right`.

The overlay is versioned separately from the frozen identity goldens in:

`benchmarks/operational_multisource_field_attribution_v1.json`

No identity value, expected resolver outcome, source definition, threshold, source qualification rule or v1 replay rule was changed to obtain the count.

## Executed operational effects

The existing v1 replay corpus first produces:

- 22 records;
- 7 CREATE;
- 7 MATCH;
- 8 REVIEW;
- 0 failed;
- 7 published vehicles.

The six Corolla Cross v2 records then execute in deterministic overlay order as:

1. CREATE;
2. MATCH;
3. MATCH;
4. CREATE;
5. MATCH;
6. REVIEW.

Combined executed effects:

- 28 replayed record-sides;
- 9 CREATE;
- 10 MATCH;
- 9 REVIEW;
- 0 failed;
- 9 published vehicles.

Every non-review Corolla Cross result is checked for preservation of its expected field-to-evidence bindings; every retained evidence reference resolves back to one of the two declared Toyota sources. Each of the six overlays also succeeds independently in a fresh store with exact CandidateFact/evidence reconstruction.

## Hosted validation

Representative integration PR #296 exact head `8961d23c22e053b1c4e97221e084fafcf2c26de2` passed hosted run `33510217638` with both required jobs and real repository steps.

Corolla Cross rollout PR #297 exact head `418482f5e4294535fd779d9ab0dff0a0751099bd` passed hosted run `33511293873` with both required jobs. The `tests` job completed checkout, harness validation, runtime health, package build/install, every isolated test and validation-evidence upload; `minimum-python` completed the isolated Python 3.11 suite.

PR #297 was squash-merged after exact-head validation.

## Residual evidence register

Current active blockers are evidence blockers, not runtime/tooling blockers.

### `EVIDENCE_BLOCKER / INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`

These remain intentionally fail-closed:

- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

Do not infer the missing field support merely to improve coverage.

### `EVIDENCE_BLOCKER / COMPOSITE_NOT_YET_ATTRIBUTED = 30`

Thirty valid composite record-sides remain outside the overlay. They should be closed in source-family batches only after every present field is defensibly bound to retained evidence.

### `EVIDENCE_GAP / ONIX_MY25_POWERTRAIN_SEMANTICS`

The retained Chevrolet MY25 price list directly supports Onix Premier Turbo 116cv, hatch body, model year 2025 and six-speed automatic transmission. The retained benchmark value is more specific: `powertrain = "1.0 turbo flex"`.

The inspected retained price-list evidence did not explicitly establish `flex`. Therefore the four BR Onix composite sides are not promoted in the current wave merely by assuming that semantic detail. Either retained/qualified evidence must explicitly close the field or the benchmark/evidence contract must be separately reconciled; no synthetic attribution is allowed.

This gap is a blocker-register line, not a reason to stop work on other source families.

## Closure-wave operating rule

Work proceeds in source-family closure waves:

1. verify all present fields against already retained/qualified evidence;
2. add only defensible overlay mappings;
3. freeze exact expected measurement deltas and runtime dispositions;
4. run every mapping independently and after the existing corpus where behavior can interact;
5. require exact-head hosted CI;
6. squash-merge only after the gate is green;
7. reconcile this execution snapshot when the authoritative count changes;
8. move evidence/tooling/runtime obstacles into the blocker register and continue unrelated families.

Do not bulk-promote all 30 remaining composite sides from their classification label alone.

## Current next lanes

- qualify T-Cross retained composite sides against Volkswagen generation/configuration/technical evidence;
- qualify Strada retained composite sides against Stellantis generation and Fiat handbook evidence;
- keep the Onix evidence gap explicit while searching only for qualified support already admissible under project source rules;
- qualify Corsa/FIPE only without elevating the retained secondary enumeration beyond its supporting role;
- process global Mustang and adjacent/incomplete families with the same field-complete evidence rule.

## Current state

`MULTISOURCE_RUNTIME = GREEN`

`REPRESENTATIVE_REPLAY = PASS`

`COROLLA_CROSS_FAMILY_ROLLOUT = PASS`

`ACTIVE_SCOPE_REPLAYABLE = 28 / 60`

`ACTIVE_SCOPE_BLOCKED = 32 / 60`

`REMAINING_COMPOSITE_NOT_YET_ATTRIBUTED = 30`

`INSUFFICIENT_RETAINED_SUPPORT = 2`

`WAVE_01 = ACTIVE_EVIDENCE_ROLLOUT`
