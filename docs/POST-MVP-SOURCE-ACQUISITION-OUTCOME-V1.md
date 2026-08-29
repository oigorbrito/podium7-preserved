# Post-MVP source acquisition outcome V1

Status: implementation prepared on synchronized stacked draft PRs; executable integration validation pending external runner recovery.

Parent mission: #122.

## Scope

PR #129 establishes the source baseline/contracts, PR #130 adds bounded NHTSA/EEA adapters, PR #131 adds bounded multi-source validation, and PR #132 adds recurring acquisition controls.

## #132 recurring acquisition controls

The coordinator:
- accepts only explicitly contracted source IDs;
- preserves existing HTTPS/host/robots/pacing enforcement;
- requires matching one-shot authorization for the exact requested locator;
- invalidates any prior pending token on every new authorization attempt, including a denied attempt;
- pins expected media type and source-specific schema signature;
- validates final host and response SHA integrity;
- emits `DRIFT` with no mutation on authorization/host/hash/media/schema drift;
- emits `UNCHANGED` with no mutation for identical content;
- emits `ACCEPTED` only for new valid content;
- bounds retries and surfaces `DEGRADED` after exhaustion;
- rejects malformed contract/checkpoint/policy/clock values fail-closed.

## Invariants preserved

No source hierarchy, evidence threshold, fusion rule, ambiguity behavior, identity-resolution rule or publication principle is changed. No new `STRONG` identifier namespace is introduced. No stealth, CAPTCHA bypass, proxy rotation or undocumented restricted-source access is added.

## Synchronization state

#131 was rebuilt directly on the current #130 head. #132 was then rebuilt directly on that synchronized #131 head. The old #132 state is retained on `backup/recurring-acquisition-128-pre-sync2-20260827`; stale global CURRENT-WORK/INDEX/TECH-DEBT edits were intentionally not copied back into the rebuilt PR.

Source terms/license drift remains the separate incremental follow-up #164/#165 and must be synchronized after #132 settles.

## Validation state

Focused deterministic regressions are committed. Repository-required executable validation is not complete because GitHub Actions hosted-runner execution remains broken under #112. Pre-step failures with `steps=null` are not test-suite results.

## Integration order after runner recovery

#129 → #130 → #131 → #132, each validated on its actual merge-candidate ancestry and squash-merged only with repository-required checks green.
