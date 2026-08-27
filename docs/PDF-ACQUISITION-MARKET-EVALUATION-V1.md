# PDF acquisition market evaluation V1

Status: decision recorded for issue #174
Decision class: `ENGINEERING_CHOICE` constrained by measured repository evidence
ADR: `ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md`

## Capability

Retain an explicitly approved automotive PDF with exact HTTPS locator, response bytes, content type, size, SHA-256 and existing content-addressed snapshot provenance so issue #168 can benchmark PDF extraction without weakening the normal acquisition path.

## Existing Podium capability

`podium7.http_acquisition` already provides:

- HTTPS-only default policy;
- DNS/non-global network-target rejection;
- redirect validation and limits;
- no-proxy acquisition;
- explicit timeout and maximum response size;
- content-type/content-encoding gates;
- exact response bytes and SHA-256;
- atomic verified content-addressed snapshots.

The measured Inmetro failure is specifically `UNSUPPORTED_CONTENT_TYPE` for `application/pdf`; it is not a missing HTTP transport or snapshot capability.

## Mature alternatives considered

### Python `urllib.request` / current Podium implementation — ADAPT

The Python standard library supports configurable openers and redirect handlers. Podium already wraps it with stricter network-target, redirect, media, size and snapshot controls. The existing `DirectHttpPolicy.allowed_content_types` is sufficient to create an explicit PDF-only profile without changing the default profile.

### Requests — REJECT migration for this gap

Requests is a mature high-level HTTP client with streaming downloads, redirect history, timeouts and TLS verification. It could acquire the same bytes. Migrating this narrow use case would add a dependency and require Podium to port/revalidate its existing DNS/non-global target policy, redirect-target checks, content gates and snapshot semantics. It does not solve a capability absent from the current stack.

## Decision

**ADAPT the existing Podium HTTP acquisition path.**

Add a bounded PDF contract that:

- accepts one exact HTTPS locator;
- uses `application/pdf` as its only allowed media type;
- disables redirects (`max_redirects=0`) so the approved locator cannot silently expand to another target;
- preserves non-global target rejection, timeout, size and encoding controls;
- reuses existing SHA-256 computation and atomic snapshot verification;
- leaves `DirectHttpPolicy()` defaults unchanged, including continued rejection of PDF.

No PDF parser, OCR engine, browser stack, external storage service or new HTTP library is introduced.

## Trade-offs

- Exact-locator/no-redirect behavior is intentionally restrictive; sources whose PDF URLs redirect require a separately evaluated contract rather than implicit relaxation.
- The standard-library stack is lower-level than Requests, but the relevant complexity is already implemented and tested in Podium.
- This decision is easily reversible because the PDF contract depends on the existing acquisition result/snapshot interfaces rather than a new storage format.

## Evidence level

The source need and existing transport failure are locally/reproducibly characterized in `COMPLIANT-ALTERNATIVE-SOURCES-V1.md`. The adapt-vs-migrate choice is an `ENGINEERING_CHOICE` under ADR-0001; any later material acquisition-stack replacement remains owner-consent gated after comparative evidence.
