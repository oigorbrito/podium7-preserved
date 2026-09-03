# PODIUM7 Productive Coverage Wave 01 — multisource rollout state

Status: active / retained through Toyota-Porsche; Corsa remains blocked

Date: 2026-09-03

Authority scope: current merged code/test state plus bounded historical probe evidence. Probe projections are never substituted for retained execution expectations or hosted certification.

## Accepted architecture

`PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

## Current retained state

Current `main`: `44b96d47685eecd34d8fb849ceead37666ec7754`.

The current retained composed measurement test asserts:

- retained record-sides: `60`;
- replayable: `56`;
- blocked: `4`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 34`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 4`.

This is the current code/test encoded retained expectation. It must not be represented as fresh hosted execution certification while hosted jobs continue to terminate before repository steps.

## Retained rollout sequence

The retained multisource sequence represented in current `main` includes:

- Corolla Cross;
- T-Cross BR;
- Strada;
- adjacent T-Cross;
- Onix;
- Mustang;
- Toyota/Porsche.

PR #309 added the final two retained Toyota/Porsche sides and the composed measurement test now asserts `56/60` replayable with `4/60` blocked.

## Remaining blocked lane

The remaining four blocked sides are the Corsa/FIPE composite cases.

PR #306 prepared a bounded evidence partition using official FIPE/TCE/DETRAN public-record evidence while explicitly excluding the prior secondary enumeration. That PR is stale relative to current `main`, asserts an obsolete retained overlay count, is marked `DO NOT MERGE`, and claims no executed coverage increment.

Therefore:

`CORSA_EVIDENCE_PREPARED = YES`

`CORSA_RETAINED = NO`

`CURRENT_REPLAYABLE = 56 / 60`

`CURRENT_BLOCKED = 4 / 60`

`60 / 60 = NOT ESTABLISHED`

## Hosted execution state

Recent hosted jobs continue to terminate without a runner and without repository steps. This condition does not establish a code failure and does not provide current-head certification.

Required certification condition:

1. exact-current-head workflow;
2. runner assigned;
3. real repository steps created;
4. required jobs execute and pass.

## Resume protocol

If Wave 01 continues:

1. recreate Corsa from then-current `main`;
2. compose every retained multisource overlay preceding it;
3. preserve the narrowed official/public-record evidence partition and continue excluding secondary enumeration unless separately qualified;
4. execute targeted regressions, full suite, harness, package-install and runtime-health checks;
5. merge only after evidence is green under the applicable execution policy;
6. remeasure the full 60-side corpus;
7. update current-state documentation from the resulting authoritative measurement.

No stale probe, projected ceiling, or pre-step hosted failure may be promoted to product authority.
