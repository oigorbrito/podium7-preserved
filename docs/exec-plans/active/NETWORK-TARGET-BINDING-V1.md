# Network Target Binding V1 execution plan

Status: active

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

## Acceptance criteria

1. All resolved addresses are validated against the network policy before connection.
2. The TCP connection receives a validated IP literal, not the hostname that was separately validated.
3. HTTPS keeps the original hostname for SNI/certificate validation.
4. Redirects repeat resolution/validation/binding independently.
5. Mixed global/private resolution and rebinding-to-private cases fail closed before connection.
6. Existing response-size/media/status semantics remain consistent with Direct HTTP V1.
7. Harness, focused tests, full CI, self-review, concurrency recheck, squash merge pass.
8. After integration, archive the plan and restore `CURRENT-WORK: none`.
