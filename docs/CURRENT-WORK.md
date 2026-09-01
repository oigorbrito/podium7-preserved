# Current work

Status: active evidence rollout

Decision status: `ACCEPTED = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

Authority:

- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen pre-mutation baseline and retained-evidence classification.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — executed single-source attribution state after PR #284.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md) — current executed multi-source rollout state.
- [`ADR-0002-DECISION-ACCEPTANCE.md`](ADR-0002-DECISION-ACCEPTANCE.md) — accepted Option B decision.
- [`PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md`](PODIUM7-OPERATIONAL-MULTISOURCE-CONTRACT-V2-DRAFT.md) — design input that seeded the executable v2 contract.

## Current executed state

Active three-dataset scope:

- retained record-sides: `60`;
- replayable: `28`;
- blocked: `32`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 6`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 30`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

Executed operational effects after the existing v1 corpus plus the Corolla Cross v2 family:

- 28 replayed record-sides;
- 9 CREATE;
- 10 MATCH;
- 9 REVIEW;
- 0 failed;
- 9 published consumer vehicles.

The two insufficient sides remain intentionally fail-closed:

- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

## Multi-source implementation state

`MULTISOURCE_RUNTIME = GREEN`

The runtime representability gap described in the older tracker has been closed through the merged implementation sequence:

- v2 parser/domain contract and deterministic validation;
- CREATE/MATCH ingestion with field-level evidence persistence;
- v1-to-v2 single-source semantic equivalence;
- dedicated multi-evidence REVIEW ingestion;
- review-cause persistence;
- CREATE/MATCH/REVIEW provenance reconstruction and fail-closed regressions;
- representative retained composite probe;
- representative overlay integration;
- complete Corolla Cross family rollout.

The remaining Wave 01 work is evidence-qualified rollout, not core v2 runtime construction.

## Current blocker register

Blockers are tracked as bounded lines and do not halt unrelated work.

### Evidence — insufficient retained support

`INSUFFICIENT_RETAINED_SUPPORT = 2`

The two sides listed above remain blocked until qualified evidence explicitly supports their missing present fields. No inference is allowed.

### Evidence — composite sides not yet attributed

`COMPOSITE_NOT_YET_ATTRIBUTED = 30`

These are valid retained multi-source observations, but classification alone is not enough to add an operational overlay. Each source-family batch must verify every present field and preserve source qualification.

### Evidence — Onix MY25 powertrain semantics

The retained Chevrolet price list supports Premier Turbo 116cv, hatch, model year 2025 and six-speed automatic transmission, but the inspected evidence does not explicitly establish the benchmark's more specific `powertrain = "1.0 turbo flex"` value.

The four BR Onix composite sides therefore remain pending evidence closure rather than receiving inferred `fieldEvidence`.

### Tooling / hosted validation

No active hosted-runner blocker. GitHub Actions is currently executing repository steps normally; #296 and #297 both passed exact-head hosted validation before merge.

## Current source-family lanes

Proceed as closure waves rather than one-record microtasks:

1. qualify and, if supported, integrate the retained T-Cross family;
2. qualify and, if supported, integrate the retained Strada family;
3. keep Onix in the evidence blocker register until `1.0 turbo flex` is explicitly supported or the evidence contract is separately reconciled;
4. qualify Corsa/FIPE without promoting the secondary source above its supporting role;
5. qualify global Mustang and remaining adjacent/incomplete composite families;
6. after each integrated family, remeasure replayability, blocked reason distribution, operational dispositions, provenance reconstruction and publication count.

Do not bulk-promote the remaining 30 sides solely because they are classified `COMPOSITE_SUPPORT`.

## Merge and validation rule

For every rollout PR:

- exact current head SHA;
- repository steps must execute;
- both required jobs must succeed;
- fix real repository failures rather than adjusting expected counts to the target;
- squash merge with expected head SHA;
- treat external/tooling blockers as blocker-register entries and continue independent work.

Current baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.
