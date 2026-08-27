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

## Incremental utility decision

`SOURCE_TERMS_DRIFT_GATE_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

The decision-relevant incremental capability is limited to:

- `SourceTermsPin` exact-locator + exact-digest contract;
- `REVIEW_REQUIRED` as a non-mutation state for unavailable, redirected, hash-mismatched or changed terms evidence; and
- terms locator/digest observability on recurring-run results.

The current PR branch also contains authorization/checkpoint/source-policy hardening that is already present in the latest #132 base. Those upstream controls are not evidence of additional value for #164 and must not be counted as part of this capability. Before integration, synchronize/reconstruct #165 so its final diff contains only the genuinely incremental terms-drift behavior plus its focused tests/documentation.

Utility rationale: source terms/reuse evidence can drift independently of source schema/content and existing #132 controls do not pin or compare the governing terms artifact. This closes a distinct governance gap while remaining fail-closed and without legal-text interpretation.

## Deterministic validation

Focused offline tests cover:

- matching pinned terms permitting the normal success path;
- changed terms requiring review and blocking mutation;
- unavailable terms evidence requiring review;
- requested-locator mismatch, final-locator redirect drift and acquisition-hash mismatch;
- invalid/non-HTTPS pins failing at contract construction; and
- sources with no terms pin preserving prior behavior.

Repository harness, isolated sequential suite and PR merge-candidate validation remain required before integration.
