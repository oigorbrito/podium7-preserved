# Bounded PDF acquisition — issue #174

Status: completed

## Goal

Close the measured raw-snapshot gap blocking #168 without weakening the default HTTP acquisition policy or creating parallel infrastructure.

## Integrated outcome

`podium7/pdf_acquisition.py` provides an exact-locator `PdfAcquisitionContract` and bounded PDF-only policy profile. It preserves the existing HTTPS/non-private-network controls, allows only `application/pdf`, keeps redirects disabled, preserves size/timeout limits, and reuses SHA-256 plus atomic content-addressed snapshot verification.

The normal `DirectHttpPolicy()` remains unchanged and does not allow PDF.

The exact Inmetro PBEV 2026 document path was subsequently exercised through the approved source-specific path and the extraction gold is now bound to retained raw bytes with SHA-256 `cb8ab26789b75a596f75ebf5f6454f30950d31ff8fff1de99ad56a502679db2b`. Therefore the original `PENDING_RAW_SNAPSHOT` blocker is closed.

## ADR-0001 decision

`docs/PDF-ACQUISITION-MARKET-EVALUATION-V1.md` records the market-first evaluation. The selected approach adapts the existing `urllib.request`-based Podium acquisition path rather than introducing a parallel HTTP stack for this narrow capability.

## Preserved boundaries

- no broad PDF enablement;
- no redirect relaxation;
- no generic arbitrary-file downloader;
- no OCR/extractor choice is implied;
- no canonical catalog write is authorized by acquisition alone;
- exact source/raw evidence and hash remain required before extraction claims.

## Closeout

`BOUNDED_PDF_ACQUISITION_UTILITY = INTEGRATED`.

The remaining ExtractBench work is comparative extraction evaluation on the evidence-bound gold. That work remains tracked separately by issue #168 and `EXTRACTBENCH-EVALUATION-168.md`.
