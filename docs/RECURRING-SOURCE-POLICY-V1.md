# Recurring Source Policy V1

Status: implemented bounded recurring-operation gate.

## Decision

Before Podium 7 schedules repeated live acquisition against a source host, that source MUST have an explicit `SourceOperationPolicy` defining the source ID, exact host, user agent, minimum host interval, and whether robots rules are required or demonstrably not applicable.

This is an `ADOPT/ADAPT` decision under ADR-0001: Podium uses Python's mature standard-library `urllib.robotparser` for robots semantics and adapts the existing repository `RateLimiter` for host pacing. No crawler, scheduler, browser, proxy, or generic acquisition platform is introduced.

## Rules

- HTTPS and exact configured host are mandatory.
- If `robots_mode=REQUIRED`, unavailable robots evidence fails closed.
- Robots disallow rules fail closed.
- `Crawl-delay` and `Request-rate`, when present for the configured user agent, can only strengthen the configured minimum interval.
- Host pacing applies even when robots are explicitly not applicable.
- Source-specific official/API rate limits remain authoritative and must be encoded at least as conservatively as the documented source limit before recurring operation.
- A one-off bounded research probe is not automatically authorization for recurring operation.
- This gate does not fetch robots.txt itself; acquisition remains a separate boundary and permanent tests remain offline.

## Nonclaims

V1 does not provide a scheduler, distributed rate limiter, robots cache/freshness policy, arbitrary-host crawling, or legal permission determination. It defines the minimum deterministic policy gate that must be satisfied before broad recurring acquisition is scheduled.

## Validation

Offline tests cover unavailable robots, disallow, crawl-delay, request-rate, host mismatch, HTTPS enforcement, robots-not-applicable mode, and host pacing.
