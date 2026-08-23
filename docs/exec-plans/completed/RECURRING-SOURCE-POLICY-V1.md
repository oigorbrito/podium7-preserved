# Recurring Source Policy V1 execution plan

Status: completed

## Outcome

Define and enforce the minimum deterministic policy required before Podium 7 schedules repeated live acquisition against a source host.

## Boundaries

- Reuse Python stdlib robots semantics and the existing Podium rate limiter; do not add crawler/scheduler infrastructure.
- Fail closed when robots are required but unavailable or disallow the locator.
- Host pacing must respect the configured floor and stronger robots crawl-delay/request-rate directives.
- Permanent tests remain offline.
- Source-specific documented API limits remain authoritative and must be encoded conservatively.

## Acceptance evidence

- PR #70 merged by squash as `ec68161ff1710485b72a2f7cf70837ca6227e42a`.
- GitHub Actions run `32667780915` completed successfully.
- Repository harness, project facts, runtime health, and isolated test suite all passed.
- Concurrency recheck showed `main` identical to the PR base before merge.
- Market-first disposition: `ADOPT/ADAPT` Python `urllib.robotparser` plus existing Podium `RateLimiter`; no new crawler/scheduler/browser infrastructure.
