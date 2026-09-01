# PODIUM7 Productive Coverage Wave 01 — post-attribution state

Status: `DECISION_REQUIRED = OPERATIONAL_REPLAY_PROVENANCE_MODEL`

This document records the executed state after PR #284. It supersedes only the pre-mutation counts and planning language in `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`; that document remains the historical baseline and evidence-classification record.

## Executed active-scope state

Scope: `catalog_identity_golden_v1.json`, `catalog_identity_golden_br_v1.json`, and `catalog_identity_br_adjacent_incomplete_v1.json`.

- record-sides: 60
- replayable: 22
- blocked: 38
- replayable rate: 22 / 60 = 36.67%
- `SOLE_CASE_SOURCE = 12`
- `EXPLICIT_FIELD_ATTRIBUTION = 10`
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36`
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`

The two intentionally insufficient sides remain fail-closed:

- `no-match-toyota-corolla-10g-vs-12g:left`
- `no-match-porsche-911-991-vs-992:left`

The 10 verified single-source mappings are now retained benchmark evidence, not a planning hypothesis.

## Executed V3 state

Including `catalog_identity_year_semantics_challenge_v1.json`:

- record-sides: 72
- replayable: 22
- blocked: 50
- `EXPLICIT_FIELD_ATTRIBUTION = 10`
- `SOLE_CASE_SOURCE = 12`
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 48`
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`

## Operational effects

Exact-head CI for PR #284 passed the complete isolated suite on Python 3.11 and Python 3.13.

Executed operational measurement during the attribution lane established:

- total replayed operational records: 22
- created: 7
- matched: 7
- review: 8
- failed: 0
- published consumer vehicles: 7

Published-field coverage on those 7 consumer vehicles:

- powertrain: 5 / 7
- transmission: 2 / 7
- body style: 5 / 7

Review disposition after provenance expansion is also regression-frozen:

- open operational reviews: 7
- durable human review: 7
- provenance-blocked dispositions: 6
- unassessed: 0
- unused dispositions: 0

## What the result proves

The bounded single-source lane achieved its theoretical ceiling exactly without changing identity values, expected outcomes, resolver thresholds, source qualification, or replay rules.

Therefore the remaining active blocker is no longer missing attribution metadata in the verified-single-source lane. The residual 38 blocked sides are:

- 36 sides with valid composite support constrained by the unique-common-source replay contract;
- 2 sides with insufficient retained support for safe unique-source attribution.

`DATA_COMPLETION_ALONE != WAVE_CLOSURE`

`FIELD_ATTRIBUTION_COMPLETE != CURRENT_INGESTION_REPRESENTABLE` for genuine composite observations remains the architecture boundary.

## Architecture boundary

PR #282 executed the naive source-specific sequential split experiment and rejected it: ingestion order changes which partial observation is published versus routed to review.

ADR-0002 therefore remains undecided between the bounded policies already documented. No multi-source runtime implementation is authorized merely because the single-source lane is complete.

The evaluation-only v2 multi-evidence contract remains a specification, not a selected implementation.

## Next sequence

1. Keep the 2 insufficient sides fail-closed unless stronger qualified evidence appears.
2. Keep the 36 composite sides unchanged until ADR-0002 selects the operational replay provenance model.
3. Compare admissible multi-source designs against the executed invariants: provenance fidelity, order independence, conflict behavior, v1 equivalence, source qualification, review semantics, and fail-closed rejection.
4. Reassess `DATA_READY` and `PRODUCT_READY` only after the architecture decision and its applicable validation; do not infer product readiness from the 22/60 replay rate alone.
