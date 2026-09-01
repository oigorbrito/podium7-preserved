# Current work

Status: active
Mode: evidence rollout
Decision: `ACCEPTED = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`
Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

## Authority
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen baseline/classification.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — executed single-source lane.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md) — current executed rollout, prepared lanes and blocker register.
- [`ADR-0002-DECISION-ACCEPTANCE.md`](ADR-0002-DECISION-ACCEPTANCE.md) — accepted Option B.

## Current executed state
The authoritative merged denominator is still 60 record-sides:
- replayable: `38`;
- blocked: `22`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 16`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 20`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

Executed effects after v1 + Corolla Cross + T-Cross + Strada v2:
- 14 CREATE;
- 14 MATCH;
- 10 REVIEW;
- 0 failed;
- 14 published vehicles.

`MULTISOURCE_RUNTIME = GREEN`

## Prepared but not authoritative
`PR #302 / ADJACENT_TCROSS_RETAINED`
- clean retained candidate for 6 adjacent T-Cross sides;
- additive source-family overlay composition keeps the existing single-overlay API compatible;
- projected measurement if validated/merged: `44 / 60 replayable`, `16 / 60 blocked`, `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 22`;
- exact-head run `33520809588` failed before any job step was created; do not merge until an exact-head run executes and passes.

`PR #303 / ADJACENT_ONIX_PROBE`
- test-only probe for 2 MY26 review sides;
- deliberately does not infer missing mechanical fields on the incomplete side;
- if validated and later retained after #302, projected measurement becomes `46 / 60 replayable`, `14 / 60 blocked`;
- run `33520999605` failed pre-step and therefore validates neither code nor evidence behavior.

`PR #304 / GLOBAL_DARK_HORSE_PROBE`
- test-only probe for 3 source-supported global Dark Horse sides;
- GT/left is excluded because generation support is not explicit enough;
- if all earlier prepared lanes and these 3 sides are later validated/retained, theoretical measurement becomes `49 / 60 replayable`, `11 / 60 blocked`;
- run `33521151656` failed pre-step and is not product evidence.

All projected counts above are planning deltas, not executed claims.

## Blocker register
Blockers are bounded lines and do not halt unrelated evidence work.

`HOSTED_CI_PRE_STEP`
Current #302/#303/#304 runs all terminated with `steps=null` in both required jobs. Do not rerun repeatedly; resume exact-head validation when the runner can execute repository steps again.

`TOOLING / PROBE_STDOUT_EXTRACTION`
The connector did not expose #301 printed stdout. Retained tests therefore use safe invariants and must not invent exact CREATE/MATCH/REVIEW distribution or a new exact published count.

`INSUFFICIENT_RETAINED_SUPPORT = 2`
- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

`EVIDENCE_GAP / ONIX_MY25 = 4 COMPOSITE SIDES`
The retained MY25 Chevrolet material does not explicitly establish benchmark `powertrain = "1.0 turbo flex"`. Do not infer `flex`.

`SOURCE_POLICY / CORSA_FIPE = 4 COMPOSITE SIDES`
Official FIPE supplies lookup/model-year semantics; concrete code/year enumeration remains secondary supporting evidence and is not promoted to identity authority for coverage gain.

`EVIDENCE_GAP / MUSTANG_GT_GENERATION = 1 COMPOSITE SIDE`
The GT side of `no-match-ford-mustang-gt-vs-dark-horse` lacks sufficiently explicit retained support for `generation = "7th generation"`.

## Resume order
1. Exact-head validate #302; if both jobs execute and pass, squash-merge with expected head SHA and close #301 as consumed evidence.
2. Re-run/validate #303 probe; if green, create a clean retained Onix source-family overlay from current `main`, target `46/14`, validate and squash-merge.
3. Re-run/validate #304; if green, retain only its 3 supported sides in a clean source-family overlay, leaving GT/left blocked.
4. Update this documentation PR once to the final actually merged measurement, run exact-head CI, then squash-merge #298.
5. Continue evidence acquisition/policy decisions for the bounded 11-side residual set; never bulk-promote it.

For every retained rollout: exact-head CI, both jobs green with real steps, no forced counts, squash merge with expected head SHA, then remeasure coverage/dispositions/provenance.

Baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.
