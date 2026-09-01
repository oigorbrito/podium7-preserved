# PODIUM7 Productive Coverage Wave 01 — multisource rollout state

Status: active / executed through Strada; all remaining sides have prepared candidates, hosted validation pending

Date: 2026-09-01

Authority scope: merged execution evidence plus a bounded register of unmerged candidate/probe lanes. Prepared projections are never substituted for executed measurements.

## Accepted architecture

`PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

The runtime lane is already green: v2 parsing, CREATE/MATCH/REVIEW multi-evidence handling, single-source equivalence, review snapshots and CandidateFact -> evidence -> source reconstruction are implemented and exercised by merged rollouts.

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

This `38 / 60` state is the only current coverage claim backed by merged execution.

## Completed hosted validation
- representative PR #296: passed;
- Corolla Cross PR #297: passed and squash-merged;
- T-Cross BR PR #299: passed and squash-merged;
- Strada PR #300: passed and squash-merged to main as `7f71e1c33a805441fc0c2832cb13dad8ebd6df9a`.

## Prepared candidate inventory

The 22 currently blocked record-sides are now fully partitioned into five bounded candidate lanes. This means evidence preparation has a candidate for every side; it does not mean those candidates have passed runtime validation.

### #302 — adjacent T-Cross retained candidate — 6 sides
- Source-family mapping is already prepared as a retained mutation.
- Projected isolated delta: 38 -> 44 replayable.
- Exact-head run `33520809588` failed before repository steps were created.

### #303 — Onix MY26 + MY25 qualification probe — 6 sides
MY26:
- generation/product identity from retained Chevrolet history;
- detailed Premier 1.0 Turbo hatch/MY26/six-speed mapping from the price list;
- incomplete side keeps absent mechanical fields absent.

MY25:
- official Onix 2025 owner-manual evidence supplies `1.0 T` plus `Etanol / Gasolina` semantics;
- retained MY25 price evidence supplies Premier Turbo 116cv, hatch, MY25 and six-speed automatic;
- no `flex` value is invented from marketing terminology.

Current head: `5e64c0043d03e61033b8bbddb9fd8964f21a1da7`.
Latest run `33522008754`: pre-step failure.
Cumulative planning ceiling after #302 plus later clean Onix retention: `50 / 60`.

### #304 — global Mustang qualification probe — 4 sides
All four previously composite Mustang sides now have an explicit primary-source partition.
- existing technical specification supplies GT/Dark Horse model/trim/body/5.0 V8 details;
- retained Dark Horse source supplies seventh-generation evidence for Dark Horse;
- added Ford Brasil primary evidence explicitly identifies Mustang GT Performance as seventh generation, coupe and 5.0 Coyote V8, closing the former GT/left gap without inference.

Current head: `b0173d27f4b73bbcf098483975d88d10cdee4467`.
Latest run `33521791360`: pre-step failure.
Cumulative planning ceiling: `54 / 60`.

### #305 — Toyota 10g + Porsche 991 primary-evidence probe — 2 sides
Toyota left:
- retained 2006 Toyota launch evidence establishes Corolla Axio, tenth generation, sedan and 1.8-litre 2ZR-FE;
- separate Toyota technical evidence explicitly establishes regular unleaded gasoline for 2ZR-FE;
- `1.8 petrol` is therefore a multi-source primary-evidence field candidate, not an inferred value.

Porsche left:
- retained Porsche history establishes type 991 / seventh generation;
- official Carrera S (991) technical specification establishes Carrera S, horizontally opposed six-cylinder powertrain and two-plus-two sport coupe body.

Head `c55fca0afc0ee39e6cf5aab11e1cccb3a0c4473f`.
Run `33525155237`: both jobs failed with `steps=null`.
Cumulative planning ceiling: `56 / 60`.

### #306 — Corsa public-record qualification probe — 4 sides
The previous source-policy blocker now has an alternative that does not promote `corsa-wind-fipe-code-secondary`:
- retained official FIPE evidence remains responsible for national lookup/model-year semantics;
- an official TCE-PR administrative FIPE table maps code `0040010` to `GM - CHEVROLET / Corsa Wind 1.0 MPFI / EFI 2p`;
- official DETRAN-RR public records provide concrete Corsa Wind observations in the relevant year/code family.

The secondary enumeration is explicitly absent from every probe record.

Head `b74a390e5291977533eb651f5318b83a8dc8de81`.
Run `33525548760`: both jobs failed with `steps=null`.
Cumulative planning ceiling if every preceding lane is independently validated and then cleanly retained: `60 / 60`.

## Prepared-state accounting

`EXECUTED_REPLAYABLE = 38 / 60`

`EXECUTED_BLOCKED = 22 / 60`

`PREPARED_CANDIDATE_SIDES = 22 / 22 BLOCKED`

`BLOCKED_SIDES_WITHOUT_PREPARED_CANDIDATE = 0`

`THEORETICAL_PREPARED_CEILING = 60 / 60`

The last value is a planning ceiling only. It is not an executed measurement, not a product-readiness claim and not permission to merge any probe.

## Current hosted blocker

`HOSTED_CI_PRE_STEP`

Runs for #302 through #306 are failing before either required job creates repository steps/logs. No repository test failure is observable in these runs. Repeated reruns are not useful while this condition persists.

No affected candidate is merged until an exact-current-head workflow obtains a runner, executes real repository steps and both `tests` and `minimum-python` pass.

## Resume / integration protocol
1. Validate and squash-merge #302 from its exact current head; remeasure authoritative main.
2. Recreate a clean retained Onix source/overlay rollout from then-current main using only mappings proven by #303; exact-head validate, merge and remeasure.
3. Recreate a clean retained Mustang rollout using #304 evidence; validate, merge and remeasure.
4. Recreate a clean retained Toyota/Porsche source-plus-overlay rollout using #305 evidence; validate, merge and remeasure.
5. Recreate a clean retained Corsa public-record rollout using #306 evidence, preserving FIPE supporting semantics and excluding the secondary enumeration; validate, merge and remeasure.
6. Execute the full 60-side measurement and operational replay on authoritative main. Only that result can establish whether the prepared 60/60 ceiling is actually reached.
7. Update #298 once to the final merged execution state, require exact-head hosted CI, then squash-merge the documentation reconciliation.

For every retained lane: current-main base, exact field/source audit, no inferred fields, exact-head hosted CI with real steps, both jobs green, squash merge with expected head SHA, then remeasure.

## Current state

`MULTISOURCE_RUNTIME = GREEN`

`COROLLA_CROSS_FAMILY_ROLLOUT = PASS`

`TCROSS_BR_FAMILY_ROLLOUT = PASS`

`STRADA_FAMILY_ROLLOUT = PASS`

`ACTIVE_SCOPE_REPLAYABLE = 38 / 60`

`ACTIVE_SCOPE_BLOCKED = 22 / 60`

`ALL_BLOCKED_SIDES_HAVE_PREPARED_CANDIDATES = YES`

`HOSTED_VALIDATION = PRE_STEP_BLOCKED`

`WAVE_01 = EVIDENCE_PREPARATION_COMPLETE / INTEGRATION_PENDING`
