# Bounded PDF acquisition — issue #174

Status: implementation prepared; executable validation pending

## Goal

Close the measured raw-snapshot gap blocking #168 without weakening the default HTTP acquisition policy or creating parallel infrastructure.

## ADR-0001 decision

`docs/PDF-ACQUISITION-MARKET-EVALUATION-V1.md` records the market-first evaluation. The decision is to adapt the existing `urllib.request`-based Podium acquisition path rather than migrate to Requests for this narrow capability.

## Implementation

`podium7/pdf_acquisition.py` defines an exact-locator `PdfAcquisitionContract` and PDF-only policy profile. It keeps HTTPS/non-private-network controls, allows only `application/pdf`, sets redirects to zero, preserves max size/timeout, and reuses existing SHA-256 plus atomic content-addressed snapshot verification.

The normal `DirectHttpPolicy()` remains unchanged and does not allow PDF.

## Utility disposition

`BOUNDED_PDF_ACQUISITION_UTILITY = INTEGRATE_AFTER_REPOSITORY_VALIDATION`

This closes a concrete measured gap rather than adding generic downloader infrastructure: Podium's existing acquisition/snapshot stack already supplies the required network, size, hash and storage controls, but the default media allowlist intentionally rejects `application/pdf`. #168 needs one exact official Inmetro PDF snapshot before its extraction gold can be evidence-bound.

The capability is useful only as an explicit source-specific profile. Broad PDF enablement, redirect relaxation, parser/OCR addition, or HTTP-stack replacement are not authorized by this disposition.

## Validation

Focused tests cover default-policy isolation, exact-locator behavior, PDF media enforcement, verified snapshot reuse and malformed contract rejection. Repository harness, sequential suite, project facts and fresh repository-hosted CI on the exact merge-candidate head are required before integration. Issue #112 is resolved.

## Next

After executable validation, acquire the exact Inmetro PBEV 2026 document through this bounded contract, freeze bytes/hash, and only then replace #168's `PENDING_RAW_SNAPSHOT` marker with exact provenance.
