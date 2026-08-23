# Recurring Source Policy V1 execution plan

Status: active

## Outcome

Define and enforce the minimum deterministic policy required before Podium 7 schedules repeated live acquisition against a source host.

## Boundaries

- Reuse Python stdlib robots semantics and the existing Podium rate limiter; do not add crawler/scheduler infrastructure.
- Fail closed when robots are required but unavailable or disallow the locator.
- Host pacing must respect the configured floor and stronger robots crawl-delay/request-rate directives.
- Permanent tests remain offline.
- Source-specific documented API limits remain authoritative and must be encoded conservatively.

## Acceptance criteria

1. Explicit source policy binds source ID, host, user agent, robots applicability, and minimum interval.
2. HTTPS/host mismatch, robots unavailable/disallow, and pacing failures are explicit.
3. Robots crawl-delay/request-rate can strengthen but never weaken configured pacing.
4. Tests are deterministic/offline.
5. Design docs record the market-first ADOPT/ADAPT decision and nonclaims.
6. Harness, full CI, self-review, concurrency recheck, squash merge pass.
7. After integration, archive plan and restore CURRENT-WORK to none.
