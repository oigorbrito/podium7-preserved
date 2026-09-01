# Current work

Status: active evidence rollout
Decision: `ACCEPTED = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`
Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

## Authority
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen baseline/classification.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — executed single-source lane.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md) — current executed rollout and blocker register.
- [`ADR-0002-DECISION-ACCEPTANCE.md`](ADR-0002-DECISION-ACCEPTANCE.md) — accepted Option B.

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

Operational effects after v1 + Corolla Cross v2:
- 28 replayed;
- 9 CREATE;
- 10 MATCH;
- 9 REVIEW;
- 0 failed;
- 9 published vehicles.

## Multi-source runtime
`MULTISOURCE_RUNTIME = GREEN`

Merged implementation covers:
- v2 parser/domain contract and deterministic fail-closed validation;
- CREATE/MATCH field-level evidence persistence;
- v1-to-v2 single-source equivalence;
- dedicated multi-evidence REVIEW path and review-cause persistence;
- CREATE/MATCH/REVIEW provenance reconstruction;
- representative retained composite probe/integration;
- complete retained Corolla Cross family rollout.

Remaining Wave 01 work is evidence-qualified corpus rollout, not core v2 runtime construction.

## Blocker register
Blockers are bounded lines and do not halt unrelated source families.

`INSUFFICIENT_RETAINED_SUPPORT = 2`
- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.
No inference is allowed to close these fields.

`COMPOSITE_NOT_YET_ATTRIBUTED = 30`
Classification alone does not authorize overlay mappings; every present field must be verified against retained/qualified evidence.

`EVIDENCE_GAP / ONIX_MY25_POWERTRAIN_SEMANTICS`
The retained Chevrolet price list supports Premier Turbo 116cv, hatch, MY2025 and six-speed automatic transmission, but inspected retained evidence does not explicitly establish benchmark `powertrain = "1.0 turbo flex"`. The four BR Onix composite sides remain pending evidence closure rather than receiving inferred attribution.

`HOSTED_CI = AVAILABLE`
Actions is executing repository steps normally; #296 and #297 passed exact-head hosted validation before merge.

## Next source-family waves
1. T-Cross: qualify/integrate retained generation + configuration evidence.
2. Strada: qualify/integrate Stellantis generation + Fiat handbook evidence.
3. Onix: remain blocked until `1.0 turbo flex` is explicitly supported or separately reconciled.
4. Corsa/FIPE: preserve the secondary source's supporting-only role.
5. Global Mustang and remaining adjacent/incomplete families: apply the same field-complete evidence rule.

For every rollout PR: exact-head CI, both jobs green, fix real failures rather than force expected counts, squash merge with expected head SHA, then remeasure coverage/dispositions/provenance.

Do not bulk-promote the remaining 30 sides solely because they are `COMPOSITE_SUPPORT`.

Baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.
