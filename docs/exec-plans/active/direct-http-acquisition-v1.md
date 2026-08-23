# Direct HTTP acquisition contract V1

Status: active — implementation and local verification complete; final documented merge-candidate validation/integration pending

## Outcome

Add a dependency-free, bounded direct HTTP acquisition primitive that can fetch one explicit source locator with deterministic safety and failure semantics, preserve byte-exact response evidence, and write an immutable local snapshot only after a successful acquisition.

## Why this unit

The retained frozen corpora now have deterministic acquisition lineage, but live acquisition/navigation/source-discovery generalization remains open. The smallest next step is not a crawler/browser/agent dependency: it is a direct HTTP transport contract with explicit URL, redirect, network-target, response-size, content-type, content-encoding, status and snapshot-write rules. This establishes a reproducible acquisition boundary without claiming JavaScript navigation, source discovery, heterogeneous-web recall or production coverage.

## Acceptance criteria

- dependency-free implementation using Python standard library only;
- HTTPS-only default policy, exact credential-free locators, no fragments;
- block loopback/private/link-local/reserved/multicast/unspecified targets by default, with an explicit controlled/test policy override;
- validate every redirect target with the same policy and cap redirect count;
- explicit timeout, network, HTTP-status, unsupported-content-type, unsupported-content-encoding, empty-body and response-too-large failures;
- request identity content encoding and reject non-identity responses rather than silently persisting undecoded bytes;
- return byte-exact response body plus final URL, redirect count, status, media type, charset and SHA-256 digest;
- atomically freeze a successful response to a new local snapshot and refuse accidental overwrite by default;
- focused deterministic tests against a loopback HTTP server, including redirects and negative paths;
- CLI for one explicit locator/snapshot operation without changing existing frozen benchmark semantics;
- keep package dependencies empty;
- document that public-internet behavior, JavaScript/browser navigation, source discovery and production source distribution remain UNKNOWN;
- integrate only after self-review, clean main concurrency check and green merge-candidate CI.

## Measured result

`LOCALLY_VERIFIED` on the deterministic loopback-server contract:

- 20 focused direct-HTTP tests cover protected URL/network defaults, exact bytes and SHA-256, redirect following/count/revalidation/limit, HTTP status, media type, content encoding, declared and streamed size limits, empty/malformed responses, timeout, verified snapshot freeze, no-clobber behavior, explicit overwrite and failure-before-snapshot semantics;
- package dependency set remains empty;
- corrected implementation-head merge-candidate run `32651448029`, job `97223589802`: Python `3.13.15`, `HARNESS PASS`, runtime health PASS, repository isolated suite `373/373` PASS, validation artifact ID `9496302717`, ZIP SHA-256 `3d561b37e97e89f051ed6b036fc61ac042bc1fb90679a5e9d0581c18d31187c2`.

An intermediate strengthened-test run correctly failed because a disallowed redirect scheme was being classified by `urllib` as an HTTP-status failure before the custom `redirect_request()` hook. The implementation was changed to validate redirect `Location` before delegating to the base redirect handler; the corrected run above passes the regression. The test was not weakened or removed.

This evidence is local to deterministic HTTP-server behavior. The DNS/network-target check is a preflight and does not pin the validated address to the connection; DNS-rebinding resistance is therefore not claimed. Public-internet compatibility, JavaScript/browser navigation, source discovery, site-specific robots/rate/politeness behavior and production source distribution remain outside this unit.

The implementation run above validates the corrected code head. Integration still requires green CI on the final documented merge candidate plus normal concurrency/self-review gates.

## Decision classification

- bounded/fail-closed acquisition boundary: `ENGINEERING_CHOICE` aligned with existing provenance and strict-validation invariants;
- HTTPS-only/default non-global-network blocking: `ENGINEERING_CHOICE` safety policy;
- exact issue/error taxonomy and limits: `ENGINEERING_CHOICE`;
- deterministic loopback-server behavior measured above: `LOCALLY_VERIFIED`;
- public-internet source compatibility, JavaScript navigation, discovery completeness and production coverage: `UNKNOWN` and outside this unit.
