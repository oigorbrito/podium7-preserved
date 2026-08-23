# Direct HTTP Acquisition V1

Status: `LOCALLY_VERIFIED` transport contract on deterministic loopback-server tests. Public-internet compatibility is not established.

## Purpose

`podium7.http_acquisition` is the dependency-free direct HTTP boundary for acquiring one explicit source locator and preserving the accepted response as byte-exact evidence. It is intentionally narrower than a crawler or browser layer.

The contract separates transport from extraction. A successful acquisition returns bytes and response metadata; downstream extraction remains responsible for interpreting those bytes. A snapshot is written only after transport validation succeeds.

## Default policy

`DirectHttpPolicy` is fail-closed by default:

- HTTPS is the only allowed scheme;
- credential-bearing URLs and fragments are rejected;
- hostname resolution must yield only globally routable addresses;
- redirects are capped at five and every redirect target is revalidated;
- the request asks for `Accept-Encoding: identity`;
- non-identity response encodings are rejected rather than silently persisted;
- accepted media types are `text/html`, `text/plain`, `application/json`, and `application/xhtml+xml`;
- timeout defaults to 15 seconds;
- accepted body size defaults to at most 2,000,000 bytes;
- only 2xx responses are accepted;
- missing/invalid response metadata, empty bodies and oversized bodies fail explicitly;
- snapshot overwrite is disabled unless requested explicitly.

A controlled policy override can allow `http` and private/loopback targets for deterministic local testing. That override is not used by the one-shot CLI defaults.

## Acquisition sequence

For one requested locator:

1. validate locator syntax and policy;
2. perform a DNS preflight and reject non-global resolved addresses unless explicitly allowed;
3. issue one GET with environment proxies disabled and identity content encoding requested;
4. revalidate each redirect target and enforce the redirect cap;
5. validate final URL, status, media type, content encoding and declared/observed body size;
6. retain the exact received bytes and compute SHA-256;
7. optionally freeze the bytes to a local snapshot;
8. verify the written digest and create the existing SHA-256 content-addressed evidence reference.

The successful result records requested URL, final URL, redirect count, status, media type, charset, byte length and SHA-256 digest. The body itself remains byte-exact in memory and is not inserted into the JSON summary payload.

## Explicit failures

The stable V1 error codes are:

- `INVALID_URL`
- `UNSAFE_NETWORK_TARGET`
- `DNS_FAILURE`
- `REDIRECT_LIMIT`
- `TIMEOUT`
- `NETWORK_ERROR`
- `HTTP_STATUS`
- `MALFORMED_RESPONSE`
- `UNSUPPORTED_CONTENT_TYPE`
- `UNSUPPORTED_CONTENT_ENCODING`
- `RESPONSE_TOO_LARGE`
- `EMPTY_BODY`
- `SNAPSHOT_EXISTS`
- `SNAPSHOT_WRITE_ERROR`

A failed acquisition does not create the requested snapshot.

## Snapshot semantics

A successful response can be frozen with `freeze_http_snapshot()` or acquired and frozen in one call with `acquire_and_freeze_http()`.

The write uses a temporary file in the destination directory, flushes and `fsync`s the bytes, and verifies the final SHA-256 against the acquisition result. With overwrite enabled the final replacement uses `os.replace`. With overwrite disabled the V1 no-clobber path uses a same-filesystem hard link so an already-existing destination wins atomically rather than being overwritten.

The no-overwrite hard-link behavior is locally verified on the current Ubuntu CI runner. Cross-filesystem/platform support has not been characterized.

## CLI

The one-shot CLI keeps the protected defaults:

```text
PYTHONPATH=. python scripts/acquire_http_snapshot.py <https-url> <snapshot-path>
```

Optional bounds are `--timeout-seconds`, `--max-bytes`, `--max-redirects`, and `--overwrite`. The CLI emits a JSON PASS/FAIL summary and returns a non-zero exit status on failure.

## Local validation

Corrected implementation-head merge-candidate run `32651448029`, job `97223589802`:

- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `373/373` PASS;
- 20 focused direct-HTTP tests are included in that total;
- validation artifact ID `9496302717`;
- artifact ZIP SHA-256 `3d561b37e97e89f051ed6b036fc61ac042bc1fb90679a5e9d0581c18d31187c2`.

The focused cases include the protected default scheme/network policy, byte preservation, redirect counting/revalidation/limit, HTTP status, media type, content encoding, declared and streamed body-size limits, empty/malformed responses, timeout, snapshot verification, no-clobber behavior, explicit overwrite and no snapshot after acquisition failure.

One intermediate strengthened-test run exposed that `urllib` could reject a disallowed redirect scheme before `redirect_request()` and therefore misclassify it as an HTTP-status failure. V1 fixes this by validating `Location` before delegating redirect handling; the corrected merge candidate above passes the regression case.

## Limits and non-claims

This work unit does **not** establish:

- public-internet source compatibility, availability or acquisition success rate;
- JavaScript execution, browser navigation or anti-bot behavior;
- source discovery or crawling completeness;
- robots-policy, crawl-delay, rate-limit or site-specific politeness behavior;
- heterogeneous-web extraction precision/recall or production source distribution;
- comprehensive SSRF protection or DNS-rebinding resistance.

The network-target check is a DNS preflight before transport. V1 does not pin the validated address to the subsequent connection, so it must not be described as a complete DNS-rebinding defense.

## Decision classification

- bounded/fail-closed direct HTTP acquisition boundary: `ENGINEERING_CHOICE`;
- HTTPS-only and non-global-target blocking by default: `ENGINEERING_CHOICE`;
- exact limits, accepted media types and failure taxonomy: `ENGINEERING_CHOICE`;
- behavior covered by the deterministic loopback-server suite: `LOCALLY_VERIFIED`;
- public-internet compatibility, browser/navigation behavior, discovery completeness and production coverage: `UNKNOWN`.
