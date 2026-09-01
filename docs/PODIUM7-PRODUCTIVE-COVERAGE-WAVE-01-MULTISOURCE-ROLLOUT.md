# PODIUM7 Productive Coverage Wave 01 — multisource rollout state

Status: active / executed through Strada family rollout

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

After the verified single-source lane plus Corolla Cross, T-Cross and Strada multi-source rollouts:
- retained record-sides: `60`;
- replayable: `38`;
- blocked: `22`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 16`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 20`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

The 16 v2 record-sides are the complete retained Corolla Cross, T-Cross and Strada composite families currently admitted into the overlay. Field attribution remains versioned separately from frozen identity goldens in `benchmarks/operational_multisource_field_attribution_v1.json`.

No identity value, expected resolver outcome, source definition, threshold, qualification rule or v1 replay rule was changed to obtain the count.

## Executed operational effects

The existing v1 replay corpus first produces:
- 22 records;
- 7 CREATE;
- 7 MATCH;
- 8 REVIEW;
- 0 failed;
- 7 published vehicles.

Corolla Cross executes as CREATE / MATCH / MATCH / CREATE / MATCH / REVIEW.
T-Cross executes with the same family-level disposition pattern.
Strada executes as CREATE / MATCH / CREATE / CREATE.

Combined executed effects:
- 38 replayed record-sides;
- 14 CREATE;
- 14 MATCH;
- 10 REVIEW;
- 0 failed;
- 14 published vehicles.

Every mapped record is exercised independently with exact CandidateFact/evidence/source reconstruction, and the family rollouts are also replayed after the existing corpus to freeze interaction-sensitive behavior.

## Hosted validation

Representative integration PR #296 passed hosted run `33510217638`.

Corolla Cross rollout PR #297 passed hosted run `33511293873` with both required jobs and was squash-merged.

T-Cross rollout PR #299 passed hosted run `33512430109`; both required jobs completed successfully and the PR was squash-merged to main.

Strada rollout PR #300 exact head `6a1f0efb4f0cf8e8f768d310a5804b5abd8d2209` passed hosted run `33514203496`; both `tests` and `minimum-python` completed successfully, including harness, dependency installation, runtime health, package build/install, isolated tests and validation evidence. PR #300 was squash-merged to main as `7f71e1c33a805441fc0c2832cb13dad8ebd6df9a`.

## Residual blocker register

### `EVIDENCE_BLOCKER / INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`
- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

Do not infer missing field support merely to improve coverage.

### `EVIDENCE_BLOCKER / COMPOSITE_NOT_YET_ATTRIBUTED = 20`
Twenty composite record-sides remain outside the retained overlay. They close only in source-family batches after every present field is defensibly bound to retained evidence.

### `EVIDENCE_GAP / ONIX_MY25_POWERTRAIN_SEMANTICS`
Retained Chevrolet evidence supports Premier Turbo 116cv, hatch body, model year 2025 and six-speed automatic transmission, but inspected retained evidence does not explicitly establish benchmark `powertrain = "1.0 turbo flex"`. The BR MY25 Onix composite sides remain blocked rather than inferred.

### `SOURCE_POLICY_BLOCKER / CORSA_FIPE`
FIPE official evidence establishes lookup/model-year semantics. The concrete Corsa code/year enumeration is retained from a secondary supporting source. Do not promote that source to sole identity authority solely to increase coverage.

### `TOOLING_NOTE / LARGE_PDF_RENDER`
The Fiat Strada handbook exceeds the visual-render path size limit. This did not block evidence closure because retained official text explicitly enumerates `VOLCANO 1.3 FLEX`, `VOLCANO 1.3 CVT FLEX` and `RANCH 1.3 CVT FLEX`, while retained Stellantis evidence establishes the second-generation Strada/pickup context.

## Qualified next lanes

### Adjacent/incomplete T-Cross
Six record-sides are field-attribution candidates using only retained official Volkswagen evidence:
- generation/body/Brazil context from `vw-tcross-brazil-generation`;
- complete Highline 250 TSI mechanical identity from launch/technical-sheet evidence;
- current-page variant identity where transmission is intentionally absent;
- MY26 year/mechanical context from the retained owner manual.

Because equivalent T-Cross entities already exist in the retained corpus, a stacked test-only probe is measuring empirical CREATE/MATCH/REVIEW interaction before any retained mutation. Do not freeze actions from intuition.

### Adjacent/incomplete Onix
The two review sides are separately qualified from the MY25 blocker: retained MY26 price-list evidence explicitly establishes Premier `1.0 Turbo`, hatch, MY2026 and six-speed automatic; the engineering article supports the intentionally incomplete Premier/hatch/MY2026 observation; generation evidence remains separate. This lane may proceed without inferring MY25 `flex` semantics.

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

## Current state

`MULTISOURCE_RUNTIME = GREEN`

`REPRESENTATIVE_REPLAY = PASS`

`COROLLA_CROSS_FAMILY_ROLLOUT = PASS`

`TCROSS_FAMILY_ROLLOUT = PASS`

`STRADA_FAMILY_ROLLOUT = PASS`

`ACTIVE_SCOPE_REPLAYABLE = 38 / 60`

`ACTIVE_SCOPE_BLOCKED = 22 / 60`

`REMAINING_COMPOSITE_NOT_YET_ATTRIBUTED = 20`

`INSUFFICIENT_RETAINED_SUPPORT = 2`

`WAVE_01 = ACTIVE_EVIDENCE_ROLLOUT`
