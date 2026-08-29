# Post-MVP source acquisition execution plan V1

Status: synchronized through #132; executable validation pending
Parent mission: #122

## Outcome

Expand Podium 7's evidence-backed automotive acquisition/enrichment layer using qualified sources without changing existing evidence, fusion, ambiguity, identity-resolution, or publication principles.

## Utility dispositions

- #129 / #123–#125: `INTEGRATE_AFTER_REPOSITORY_VALIDATION` — measured gaps, source qualification and NHTSA/EEA semantic contracts.
- #130 / #126: `INTEGRATE_AFTER_VALIDATION` — bounded NHTSA/EEA adapters with durable raw evidence, retained snapshot location for EEA refs and duplicate source-record rejection.
- #131 / #127: `INTEGRATE_AFTER_VALIDATION` — bounded corroboration/conflict/abstention harness; provenance completeness applies only to candidate-bearing cases, expected 4/4 rather than vacuous 6/6.
- #132 / #128: `INTEGRATE_AFTER_VALIDATION` — recurring-source authorization, drift/idempotency/retry/degraded behavior; denied later authorization invalidates earlier one-shot permission.

These are utility decisions, not executable PASS.

## Current ancestry

The stack was reconstructed in dependency order on 2026-08-27:

1. #130 current adapter head;
2. #131 rebuilt directly on current #130;
3. #132 rebuilt directly on current #131.

The previous #132 state remains preserved as `backup/recurring-acquisition-128-pre-sync2-20260827`. Stale global `CURRENT-WORK`, `INDEX` and `TECH-DEBT` edits from that branch were intentionally not copied back into the rebuilt PR.

Follow-ups #147 and #165 depend on #131/#132 respectively and must be checked/synchronized against these rebuilt heads before integration validation.

## Boundaries

- no source/evidence/fusion/identity/publication policy changes;
- no stealth/proxy/CAPTCHA bypass;
- no manufacture/model-year semantic collapse;
- EEA regulatory variant is not retail trim;
- missing/conflicting evidence remains explicit;
- no broad source research without a measured gap.

## Validation

Repository harness, focused tests, sequential suite and merge-candidate CI remain mandatory. GitHub-hosted Actions issue #112 still prevents executable integration evidence; pre-step failures are not test failures.

Integration order remains #129 → #130 → #131 → #132, with squash merge only after actual validation on the synchronized ancestry.
