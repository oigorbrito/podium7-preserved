# PODIUM7 Productive Coverage Wave 01 — multisource rollout state

Status: active / executed through T-Cross family rollout

Date: 2026-09-01

Authority scope: executed post-ADR-0002 operational multi-source coverage state. This document supersedes the post-single-source count as the current Wave 01 execution snapshot; the frozen pre-mutation classification remains in `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`.

## Decision and runtime status

Accepted architecture decision:

`PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

The runtime lane is green:
- v2 operational provenance contract/parser is implemented;
- CREATE and MATCH preserve field-level multi-evidence bindings;
- v1-to-v2 single-source semantic equivalence is covered;
- REVIEW has a dedicated multi-evidence path;
- review-cause snapshots preserve multi-source evidence context;
- CandidateFact -> evidence -> source reconstruction is tested;
- representative composite replay passed before family rollout.

Remaining work is evidence-qualified corpus rollout, not basic runtime representability.

## Executed active-scope measurement

Three retained Wave 01 datasets remain the denominator:
- `catalog_identity_golden_v1.json`;
- `catalog_identity_golden_br_v1.json`;
- `catalog_identity_br_adjacent_incomplete_v1.json`.

After the verified single-source lane plus Corolla Cross and T-Cross multi-source rollouts:
- retained record-sides: `60`;
- replayable: `34`;
- blocked: `26`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 12`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 24`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

The 12 v2 record-sides are the complete retained Corolla Cross and T-Cross composite families in `catalog_identity_golden_br_v1.json`. Their field attribution remains versioned separately from frozen identity goldens in `benchmarks/operational_multisource_field_attribution_v1.json`.

No identity value, expected resolver outcome, source definition, threshold, qualification rule or v1 replay rule was changed to obtain the count.

## Executed operational effects

The existing v1 replay corpus first produces:
- 22 records;
- 7 CREATE;
- 7 MATCH;
- 8 REVIEW;
- 0 failed;
- 7 published vehicles.

Corolla Cross then executes as CREATE / MATCH / MATCH / CREATE / MATCH / REVIEW.
T-Cross executes with the same family-level disposition pattern.

Combined executed effects:
- 34 replayed record-sides;
- 11 CREATE;
- 13 MATCH;
- 10 REVIEW;
- 0 failed;
- 11 published vehicles.

Every mapped record is exercised independently with exact CandidateFact/evidence/source reconstruction, and the family rollouts are also replayed after the existing corpus to freeze interaction-sensitive behavior.

## Hosted validation

Representative integration PR #296 exact head `8961d23c22e053b1c4e97221e084fafcf2c26de2` passed hosted run `33510217638`.

Corolla Cross rollout PR #297 exact head `418482f5e4294535fd779d9ab0dff0a0751099bd` passed hosted run `33511293873` with both required jobs and was squash-merged.

T-Cross rollout PR #299 exact head `58ec8cb0f39ae448a0c47c8099dfbc846939e80a` passed hosted run `33512430109`; both `tests` and `minimum-python` completed successfully, including harness, dependency installation, runtime health, package build/install, isolated tests and validation evidence. PR #299 was squash-merged to main as `e8c102058c9102ce380309f3d104bd7cd15db6fe`.

## Residual blocker register

### `EVIDENCE_BLOCKER / INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`
- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

Do not infer missing field support merely to improve coverage.

### `EVIDENCE_BLOCKER / COMPOSITE_NOT_YET_ATTRIBUTED = 24`
Twenty-four composite record-sides remain outside the overlay. They close only in source-family batches after every present field is defensibly bound to retained evidence.

### `EVIDENCE_GAP / ONIX_MY25_POWERTRAIN_SEMANTICS`
Retained Chevrolet evidence supports Premier Turbo 116cv, hatch body, model year 2025 and six-speed automatic transmission, but inspected retained evidence does not explicitly establish the benchmark value `powertrain = "1.0 turbo flex"`. The BR Onix composite sides remain blocked rather than inferred.

### `SOURCE_POLICY_BLOCKER / CORSA_FIPE`
FIPE official evidence establishes lookup/model-year semantics. The concrete Corsa code/year enumeration is retained from a secondary supporting source. Do not promote that source to sole identity authority solely to increase coverage.

### `TOOLING_NOTE / LARGE_PDF_RENDER`
The Fiat Strada handbook exceeds the visual-render path size limit. This is not an evidence blocker: retained official text explicitly enumerates `VOLCANO 1.3 FLEX`, `VOLCANO 1.3 CVT FLEX` and `RANCH 1.3 CVT FLEX`, while retained Stellantis evidence establishes the second-generation Strada/pickup/1.3 Firefly context.

## Closure-wave operating rule

Work proceeds in source-family closure waves:
1. verify all present fields against retained/qualified evidence;
2. add only defensible overlay mappings;
3. freeze expected measurement deltas and runtime dispositions;
4. run mappings independently and after the existing corpus where behavior can interact;
5. require exact-head hosted CI;
6. squash-merge only after both jobs are green;
7. reconcile this execution snapshot when the authoritative count changes;
8. move evidence/tooling/runtime obstacles into the blocker register and continue unrelated families.

Do not bulk-promote remaining composite sides from classification labels alone.

## Current next lanes

1. Strada — integrate the qualified Stellantis generation + Fiat handbook family.
2. Onix — remain blocked until the powertrain semantic gap closes explicitly.
3. Corsa/FIPE — preserve the secondary source's supporting-only role.
4. Mustang — continue field qualification; PDF rendering is a tooling line, not a project stop.
5. Remaining adjacent/incomplete source families — apply the same field-complete rule.

## Current state

`MULTISOURCE_RUNTIME = GREEN`

`REPRESENTATIVE_REPLAY = PASS`

`COROLLA_CROSS_FAMILY_ROLLOUT = PASS`

`TCROSS_FAMILY_ROLLOUT = PASS`

`ACTIVE_SCOPE_REPLAYABLE = 34 / 60`

`ACTIVE_SCOPE_BLOCKED = 26 / 60`

`REMAINING_COMPOSITE_NOT_YET_ATTRIBUTED = 24`

`INSUFFICIENT_RETAINED_SUPPORT = 2`

`WAVE_01 = ACTIVE_EVIDENCE_ROLLOUT`
