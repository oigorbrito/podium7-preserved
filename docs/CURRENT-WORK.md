# Current work

Status: active

Mode: evidence rollout / hosted validation pending

Decision: `ACCEPTED = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

Active product-evolution blocks:

- `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01` — retained multisource rollout, currently encoded at 60/60 replayable with Corsa retained.
- `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-02` — Brazilian quantitative technical-sheet readiness evaluation; current decision remains data-not-ready for the V1 quantitative publication contract.

## Authority

- [`PROJECT-STATE.md`](PROJECT-STATE.md) — baseline/project authority outside active product-evolution blocks.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen pre-mutation Wave 01 boundary.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — earlier executed attribution state.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md) — current retained multisource rollout state.
- [`ADR-0002-DECISION-ACCEPTANCE.md`](ADR-0002-DECISION-ACCEPTANCE.md) — accepted field-level multisource decision.

Authority rule:

`CODE/TEST ENCODED RETAINED EXPECTATION != CURRENT-HEAD HOSTED EXECUTION CERTIFICATION`

## Current retained multisource state

The retained composed measurement test on current `main` asserts:

- retained record-sides: `60`;
- replayable: `56`;
- blocked: `4`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 34`;
- blocked reason: `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 4`.

Retained rollout sequence represented in `main` includes Corolla Cross, T-Cross, Strada, adjacent T-Cross, Onix, Mustang, and Toyota/Porsche.

The four remaining blocked sides are the Corsa/FIPE composite cases. PR #306 contains bounded public-record evidence preparation, but its test head is stale and explicitly `DO NOT MERGE`. No Corsa coverage increment is claimed from that probe.

## Hosted execution state

GitHub-hosted workflow jobs continue to fail before repository execution: affected jobs receive no runner and expose no repository steps. These failures are infrastructure failures, not code-test failures.

Do not promote hosted certification until an exact-current-head workflow obtains a runner, creates real steps, and completes the required repository checks.

## Next sequence

1. Preserve Wave 02 (#311) as the current quantitative-readiness execution candidate; do not merge until current-head execution evidence exists.
2. Archive stale documentation reconciliation PR #298 after this replacement reconciliation is established.
3. Archive stale Corsa probe PR #306 as evidence-only; the retained Corsa rollout now exists on current `main` and composes the complete retained overlay set.
4. If Wave 01 continues, keep the retained Corsa overlay aligned with current authority and preserve `60/60` on exact-current-head local execution.
5. Reconcile current-state documentation again after any retained Corsa integration or after hosted CI certification changes.

No planning ceiling or stale probe is product authority.
