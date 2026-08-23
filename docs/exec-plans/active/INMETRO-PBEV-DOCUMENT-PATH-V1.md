# Inmetro PBEV Document Path V1 execution plan

Status: active

## Outcome

Establish a deliberate current Inmetro PBEV PDF acquisition-and-table-extraction path without weakening the global HTTP media-type policy.

## Current official evidence

On 2026-08-23 the official Inmetro vehicle table page exposed the 2026 18th-cycle PDF, updated 2026-08-19, and the PDF itself reported an update date of 2026-08-14 with hundreds of current vehicle rows. The Inmetro FAQ also states that a CSV is available through dados.gov.br, but that catalog surface remains JavaScript-mediated and earlier direct API characterization was not a stable unauthenticated current-vehicle path.

## Market-first decision

ADR-0001 applies to document extraction. Mature choices considered: pdfplumber, pypdf, Camelot and Tabula. The current PBEV artifact is a line-ruled table PDF; V1 `ADOPT`s pdfplumber because it provides bounded table extraction directly in Python without adding a JVM or a separate browser/document service. The existing bound HTTP transport is reused for acquisition. Classification: `ENGINEERING_CHOICE` backed by the inspected current document shape.

## Boundaries

- Only `https://www.gov.br` is accepted by the Inmetro acquisition helper.
- The source-specific policy allows only `application/pdf`; the global Direct HTTP defaults remain unchanged.
- The arbitrary-locator acquisition path remains DNS-rebinding-resistant.
- Extraction promotes only table identity/source evidence: category, make, model, version, engine label, propulsion label and fuel code.
- No consumption, emissions or efficiency semantics are normalized in V1.
- Permanent tests are offline/deterministic; live current-source evidence is documentation evidence, not a CI dependency.

## Acceptance criteria

1. Source-specific PDF acquisition policy does not widen global media types.
2. Non-Inmetro hosts fail before network access.
3. PDF table extraction uses a mature library selected under ADR-0001.
4. Multi-row headers and source coordinates are retained deterministically.
5. Malformed/non-PDF or unrecognized table content fails explicitly.
6. Docs record current official evidence and semantic nonclaims.
7. Harness, full isolated suite, PR CI, self-review, concurrency recheck and squash merge pass.
8. After integration, archive the plan, clear CURRENT-WORK and close the bounded Inmetro path debt.
