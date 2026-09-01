# PODIUM7 Productive Coverage Wave 01 — multisource rollout state

Status: active / executed through Strada; later source-family lanes prepared but not yet authoritative

Date: 2026-09-01

Authority scope: executed post-ADR-0002 operational multi-source coverage state plus a bounded register of prepared, unmerged lanes. Projections are never substituted for executed measurements.

## Accepted architecture

`PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

The runtime lane is green: v2 parsing, CREATE/MATCH/REVIEW multi-evidence handling, single-source equivalence, review snapshots and CandidateFact -> evidence -> source reconstruction are implemented and already exercised by merged family rollouts.

## Executed authoritative measurement

The three retained Wave 01 datasets remain the denominator:
- `catalog_identity_golden_v1.json`;
- `catalog_identity_golden_br_v1.json`;
- `catalog_identity_br_adjacent_incomplete_v1.json`.

Merged state after the single-source lane plus Corolla Cross, T-Cross BR and Strada:
- retained record-sides: `60`;
- replayable: `38`;
- blocked: `22`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 16`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 20`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

Executed operational effects:
- 14 CREATE;
- 14 MATCH;
- 10 REVIEW;
- 0 failed;
- 14 published vehicles.

This is the only count currently claimable as merged execution evidence.

## Completed hosted validation
- representative PR #296: hosted CI passed;
- Corolla Cross PR #297: hosted CI passed and squash-merged;
- T-Cross BR PR #299: hosted CI passed and squash-merged;
- Strada PR #300: hosted CI passed and squash-merged to main as `7f71e1c33a805441fc0c2832cb13dad8ebd6df9a`.

## Prepared source-family lanes

### #302 — adjacent T-Cross retained candidate
Six field-complete adjacent/incomplete T-Cross sides were previously exercised by test-only probe #301. The retained candidate is cleanly based on current `main`, keeps the existing v1 overlay unchanged, and adds an additive overlay-set composition helper plus a source-family overlay.

Projected only if exact-head validation later succeeds:
- replayable `44 / 60`;
- blocked `16 / 60`;
- v2 method `22`;
- residual reason codes: 14 multi-source without retained attribution + 2 missing-side attribution.

No exact CREATE/MATCH/REVIEW distribution is claimed because the current connector could not recover #301 printed stdout. The retained regression uses safe invariants instead of invented outputs.

Run `33520809588` for #302 failed before either job created repository steps. That is a hosted-execution blocker, not a test failure.

### #303 — adjacent Onix MY26 probe
Two review sides are evidence-separable from the MY25 blocker:
- second-generation identity from retained Chevrolet product history;
- detailed Premier 1.0 Turbo hatch/MY26/six-speed configuration from the official price list;
- intentionally incomplete Premier/hatch/MY26 context from the engineering article, without fabricating missing powertrain/transmission.

If the probe becomes green and a later clean retained overlay is validated after #302, the projected measurement is `46 / 60 replayable`, `14 / 60 blocked`.

Run `33520999605` failed pre-step; no probe result is claimed yet.

### #304 — three-side global Dark Horse probe
The two sides of `match-ford-mustang-dark-horse` and the Dark Horse/right side of `no-match-ford-mustang-gt-vs-dark-horse` have a defensible field split between Ford technical specification evidence and separate seventh-generation Dark Horse evidence.

The GT/left side is explicitly excluded because its `generation = "7th generation"` field is not sufficiently supported by the retained sources without inference.

If all prior prepared lanes plus these three sides are eventually validated and retained, the theoretical ceiling becomes `49 / 60 replayable`, `11 / 60 blocked`. This is not an executed result.

Run `33521151656` failed pre-step; no probe result is claimed yet.

## Current hosted blocker

`HOSTED_CI_PRE_STEP`

The exact-head runs for #302, #303 and #304 all terminated with both required jobs failing before steps/logs were created. Repeated reruns are not useful while this condition persists. The engineering wave continues through evidence classification and preparation, but no affected PR is merged until a fresh exact-head run executes repository steps and both jobs pass.

## Residual evidence/policy register

If the three prepared lanes above all eventually pass and are retained, the bounded residual set is 11 record-sides:
- 2 insufficient retained-support sides: Toyota Corolla 10g left and Porsche 991 left;
- 4 BR Onix MY25 composite sides blocked on explicit `1.0 turbo flex` semantics;
- 4 Corsa/FIPE composite sides blocked on source-authority policy;
- 1 Mustang GT composite side blocked on explicit seventh-generation support.

This residual is a planning classification, not a permission to weaken evidence rules.

## Closure-wave operating rule
1. verify all present fields against retained/qualified evidence;
2. isolate a source-family candidate or test-only probe;
3. freeze measurement deltas but do not invent runtime dispositions;
4. validate independently and after the retained corpus when interaction matters;
5. require exact-head hosted CI with real steps;
6. squash-merge only after both jobs are green;
7. reconcile authority only from merged execution evidence;
8. record CI/runtime/tooling/evidence obstacles as blocker-register lines and continue unrelated work.

## Current state

`MULTISOURCE_RUNTIME = GREEN`

`COROLLA_CROSS_FAMILY_ROLLOUT = PASS`

`TCROSS_BR_FAMILY_ROLLOUT = PASS`

`STRADA_FAMILY_ROLLOUT = PASS`

`ACTIVE_SCOPE_REPLAYABLE = 38 / 60`

`ACTIVE_SCOPE_BLOCKED = 22 / 60`

`TCROSS_ADJACENT_RETAINED = PREPARED / CI_PRE_STEP_BLOCKED`

`ONIX_ADJACENT_PROBE = PREPARED / CI_PRE_STEP_BLOCKED`

`GLOBAL_DARK_HORSE_PROBE = PREPARED / CI_PRE_STEP_BLOCKED`

`WAVE_01 = ACTIVE_EVIDENCE_ROLLOUT`
