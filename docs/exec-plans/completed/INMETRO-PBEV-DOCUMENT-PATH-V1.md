# Inmetro PBEV Document Path V1 execution plan

Status: completed

## Outcome

Established a deliberate current Inmetro PBEV PDF acquisition-and-table-extraction path without weakening the global HTTP media-type policy.

## Current official evidence

On 2026-08-23 the official Inmetro vehicle table page exposed the 2026 18th-cycle PDF, updated 2026-08-19, and the PDF itself reported an update date of 2026-08-14 with hundreds of current vehicle rows. The Inmetro FAQ also states that a CSV is available through dados.gov.br, but that catalog surface remains JavaScript-mediated and earlier direct API characterization was not a stable unauthenticated current-vehicle path.

## Market-first decision

ADR-0001 applied to document extraction. Mature choices considered: pdfplumber, pypdf, Camelot and Tabula. V1 `ADOPT`s pdfplumber as optional `pbev` functionality because the current PBEV artifact is a line-ruled table PDF. The core package remains dependency-free, and the existing bound HTTP transport is reused for acquisition. Classification: `ENGINEERING_CHOICE` backed by the inspected current document shape.

## Boundaries delivered

- only `https://www.gov.br` is accepted by the Inmetro acquisition helper;
- source-specific policy accepts only `application/pdf`; global Direct HTTP defaults are unchanged;
- acquisition reuses the DNS-rebinding-resistant bound path;
- extraction emits only category, make, model, version, engine label, propulsion label, fuel code, source URL, page and row;
- no consumption, emissions or efficiency semantics are normalized;
- pdfplumber is lazy-loaded and declared only in the optional `pbev` extra, preserving the core dependency-free contract;
- permanent tests remain offline/deterministic.

## Validation result

PR #74 was merged by squash after repository harness, facts generation, runtime health and the complete isolated suite passed on GitHub Actions run `32669145640` (429/429 tests). Two integration failures were found and corrected before merge: eager optional-dependency import in checkout-only CI, and an attempted core dependency that violated the repository's dependency-free packaging invariant. Final implementation commit before merge: `18bc61642593941832c853f358ca2db860710d23`; squash merge: `579ad3dfb1d567ab69e577f974856b8528e220c5`.
