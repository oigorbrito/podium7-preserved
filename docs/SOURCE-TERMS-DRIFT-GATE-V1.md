# Source Terms Drift Gate V1

Status: implementation proposed by issue #164; integration pending repository validation.

## Documentation basis

Donor evaluation #162 identified VehiclesDB's pinned-license drift gate as a mature pattern not yet represented in Podium's recurring-source controls. Podium already fails closed on host, content-hash, media-type and schema drift. This gate adds an independent terms/reuse-artifact drift check without changing source/evidence semantics.

## Contract

A recurring source may optionally declare a `SourceTermsPin` containing:

- an exact HTTPS locator for the governing terms/license artifact; and
- the SHA-256 digest of the exact inspected artifact bytes.

A source without an applicable external terms artifact may omit the pin and preserves the existing recurring-acquisition behavior.

## Runtime behavior

Before a successful recurring acquisition becomes mutation-eligible for a pinned source:

1. terms evidence must be supplied;
2. its requested locator must equal the pinned locator;
3. its final locator after redirects must still equal the pinned locator;
4. its body must match its recorded acquisition hash; and
5. the exact body SHA-256 must equal the pinned expected digest.

Failure of any terms check produces `REVIEW_REQUIRED` with `mutation_required=false`. Terms drift or redirect drift is therefore an operational/compliance review state, not a source-data conflict and not an automatic legal conclusion.

Existing host/content/media/schema drift continues to produce `DRIFT`.

## Nonclaims

- Hash equality does not establish legal permission or license compatibility.
- The gate does not interpret legal text.
- The gate does not select sources or change evidence strength.
- The gate does not fetch terms itself or add a crawler/scheduler.
- Software repository licenses, source-data reuse terms and statutory/public-sector access bases remain distinct concepts.

## Deterministic validation

Focused offline tests cover:

- matching pinned terms permitting the normal success path;
- changed terms requiring review and blocking mutation;
- unavailable terms evidence requiring review;
- requested-locator mismatch, final-locator redirect drift and acquisition-hash mismatch;
- invalid/non-HTTPS pins failing at contract construction; and
- sources with no terms pin preserving prior behavior.

Repository harness, isolated sequential suite and PR merge-candidate validation remain required before integration.
