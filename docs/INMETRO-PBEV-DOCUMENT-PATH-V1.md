# Inmetro PBEV Document Path V1

Status: implemented bounded source-specific document path.

## Current source observation

The official Inmetro PBE Veicular page was checked on 2026-08-23. It exposed the 2026 18th-cycle vehicle table as a PDF and showed the resource updated on 2026-08-19. The inspected PDF reported an internal update date of 2026-08-14 and contained the current vehicle table with category, make, model, version, engine, propulsion, fuel, consumption, emissions and efficiency columns.

The official Inmetro FAQ also points to a CSV dataset at dados.gov.br. That catalog remains a JavaScript-mediated surface and the earlier direct dataset-detail locator characterized by Podium was not a stable unauthenticated current-vehicle feed. V1 therefore chooses the current official PDF deliberately rather than weakening validation or pretending the catalog is a machine-readable current endpoint.

## Decision

`pdfplumber` is `ADOPT` for the table-document extraction boundary. `pypdf`, Camelot and Tabula were considered. The PBEV document is a ruled table PDF, so pdfplumber provides the narrow capability needed without a JVM or browser/document service. Acquisition `ADAPT`s the existing bound HTTP transport and uses a source-specific `DirectHttpPolicy` that accepts only `application/pdf` from `www.gov.br`.

The global Direct HTTP policy is unchanged.

## Extracted semantics

V1 emits source evidence only for:

- category;
- make;
- model;
- version;
- engine label;
- propulsion label;
- fuel code;
- source URL, page number and row number.

These fields are not canonical identity proof by themselves. V1 does not normalize fuel codes, consumption, CO2, energy consumption, range or efficiency grades. Those require separate semantic benchmarks before promotion.

## Failure behavior

- non-HTTPS or non-`www.gov.br` locator: explicit `INVALID_URL` before transport;
- non-PDF media type: rejected by the source-specific HTTP policy;
- payload without a PDF signature: explicit extraction failure;
- document without a recognized PBEV table/header: explicit extraction failure;
- rows missing make or model: not emitted as vehicle records.

## Validation boundary

Permanent tests are deterministic and offline. They exercise the source-specific media policy, host binding, multi-row Portuguese header recognition, row provenance, malformed payloads and unrecognized tables. Current live-source inspection is evidence for source selection, not a permanent public-network CI gate.
