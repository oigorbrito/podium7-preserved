# Network Target Binding V1 execution plan

Status: completed

## Outcome

Provide a bounded HTTP acquisition path that prevents DNS rebinding between target validation and socket connection for arbitrary untrusted locators.

## Boundaries

- Resolve each hop once inside the bound transport, reject any disallowed address, then connect only to one of those validated IP literals.
- Preserve the original hostname for HTTP Host and TLS SNI/certificate verification.
- Re-resolve and revalidate every redirect hop.
- Reuse Python stdlib `socket`, `ssl`, and `http.client`; do not add proxy/browser/crawler/network-platform dependencies.
- Keep existing `acquire_http` semantics unchanged for already trusted/controlled locators; arbitrary untrusted locators must use the bound entry point.
- Permanent tests remain offline/deterministic.

## Market-first decision

Mature options considered: the existing stdlib `urllib` transport, Requests/urllib3, and HTTPX. The requirement is narrower than replacing the HTTP stack: Podium needs validation and the actual TCP connection to use the same resolved IP while retaining hostname-based TLS verification. Adding another HTTP client solely for this binding invariant would expand dependencies and still require an integration-specific resolver/connection hook. V1 therefore `ADAPT`s the stdlib connection primitives already in use. Classification: `ENGINEERING_CHOICE` constrained by the existing minimal transport contract.

## Final evidence

- PR: #72
- Final PR head: `bec11fcfeea0f1c115d25087984a1ff5e7142459`
- Official CI run: `32668431881` — PASS
- Harness: PASS
- Runtime health: PASS
- Sequential isolated suite: PASS
- Concurrency recheck: `main` remained identical to base `51245f145e2d061b00ac60cb7b01099b8106e2d3`
- Squash merge: `cdfe9c845897b3fbe5cdec21c1177b69f41015da`
- Self-review correction before merge: redirect bodies are not consumed, avoiding an unbounded redirect-body read.

All acceptance criteria passed. Network target binding is no longer open debt for the bounded arbitrary-untrusted-locator acquisition path.
