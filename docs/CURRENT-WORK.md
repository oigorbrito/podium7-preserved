# Current work

Status: active
Mode: evidence rollout
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
- replayable: `34`;
- blocked: `26`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 12`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 24`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`.

Operational effects after v1 + Corolla Cross + T-Cross v2:
- 34 replayed;
- 11 CREATE;
- 13 MATCH;
- 10 REVIEW;
- 0 failed;
- 11 published vehicles.

## Multi-source runtime
`MULTISOURCE_RUNTIME = GREEN`

Merged implementation covers v2 fail-closed parsing, CREATE/MATCH field-level evidence, single-source equivalence, multi-evidence REVIEW, provenance reconstruction, the representative probe, and complete retained Corolla Cross and T-Cross family rollouts.

Remaining Wave 01 work is evidence-qualified corpus rollout, not core v2 runtime construction.

## Blocker register
Blockers are bounded lines and do not halt unrelated source families.

`INSUFFICIENT_RETAINED_SUPPORT = 2`
- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.
No inference is allowed to close these fields.

`COMPOSITE_NOT_YET_ATTRIBUTED = 24`
Every present field must be verified against retained/qualified evidence before an overlay is added.

`EVIDENCE_GAP / ONIX_MY25_POWERTRAIN_SEMANTICS`
Retained Chevrolet evidence supports Premier Turbo 116cv, hatch, MY2025 and six-speed automatic, but does not explicitly establish benchmark `powertrain = "1.0 turbo flex"`; BR Onix composite sides remain pending rather than inferred.

`SOURCE_POLICY_BLOCKER / CORSA_FIPE`
FIPE official evidence supplies lookup/model-year semantics, while concrete code/year enumeration is retained from a secondary supporting source. Do not elevate that source to sole identity authority merely to increase coverage.

`TOOLING_NOTE / LARGE_PDF_RENDER`
The Fiat Strada handbook exceeded the visual-render path size limit, but its retained official text is available and explicitly enumerates Volcano 1.3 Flex, Volcano 1.3 CVT Flex and Ranch 1.3 CVT Flex configurations. This does not block the Strada source-family wave.

`HOSTED_CI = AVAILABLE`
PR #299 exact head `58ec8cb0f39ae448a0c47c8099dfbc846939e80a` passed both required jobs and was squash-merged.

## Next source-family waves
1. Strada: integrate retained Stellantis generation + Fiat handbook evidence.
2. Onix: remain blocked until `1.0 turbo flex` is explicitly supported or separately reconciled.
3. Corsa/FIPE: preserve the secondary source's supporting-only role.
4. Global Mustang: continue field qualification; PDF rendering limitations remain a tooling line, not a global stop.
5. Remaining adjacent/incomplete families: apply the same field-complete evidence rule.

For every rollout PR: exact-head CI, both jobs green, fix real failures rather than force counts, squash merge with expected head SHA, then remeasure coverage/dispositions/provenance.

Do not bulk-promote the remaining 24 composite sides solely because they are `COMPOSITE_SUPPORT`.

Baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.
