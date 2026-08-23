# Current work

Status: active

Outcome: add a DNS-rebinding-resistant HTTP acquisition path for arbitrary untrusted locators by resolving, validating, and connecting to the same IP address.

Boundaries: preserve TLS hostname/SNI verification; no proxy/browser/crawler; reuse stdlib transport primitives; current trusted-locator direct HTTP path remains unchanged.

Acceptance: bound transport, redirect re-resolution, offline regression tests, market-first decision record, green CI, concurrency recheck, squash merge.

Plan: `exec-plans/active/NETWORK-TARGET-BINDING-V1.md`.
