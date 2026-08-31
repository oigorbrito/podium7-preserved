# Podium 7 Requirements

Status: current requirement baseline

## Requirement groups

### REQ-FUNC

- `REQ-FUNC-001`: The system must support evidence-backed automotive acquisition, integration, reconciliation, review, and export.
- `REQ-FUNC-002`: The system must preserve conservative identity resolution and fail closed on ambiguity.
- `REQ-FUNC-003`: The system must preserve canonical persistence and evidence provenance.
- `REQ-FUNC-004`: The system must expose a private operator review workflow.

### REQ-DATA

- `REQ-DATA-001`: Source evidence must remain inspectable after canonical values exist.
- `REQ-DATA-002`: Conflicting evidence must not be silently discarded.
- `REQ-DATA-003`: Manufacture year and model year remain distinct dimensions.
- `REQ-DATA-004`: Quantitative enrichment must not drive identity matching.

### REQ-OPS

- `REQ-OPS-001`: A clean private installation and first-run health check must be documented and runnable.
- `REQ-OPS-002`: Operational readiness must be verifiable by repository scripts.
- `REQ-OPS-003`: The repository must clearly distinguish local operational acceptance from hosted certification state.
- `REQ-OPS-004`: Backup and restore boundaries must be explicit.

### REQ-QUAL

- `REQ-QUAL-001`: Quality gates must cover functional suitability, reliability, operability, maintainability, security, installation, persistence, provenance, recovery, and testing.
- `REQ-QUAL-002`: Benchmarks and regression checks must support the resolver and pipeline decisions.
- `REQ-QUAL-003`: Validation must remain reproducible and tied to the exact repository state under test.

## Current non-scope

- public distribution or licensing change;
- weakening conservative identity resolution;
- product changes imported from other repositories without Podium7 evidence;
- hosted certification as a replacement for local baseline acceptance.
- live acquisition as a requirement for the current private baseline;
  fixture-backed operation is acceptable while validation remains
  repeatable and evidence-backed.

## Traceability

- `REQ-FUNC-002` -> `podium7.identity`, `podium7.catalog_resolution_precedence` -> identity regression tests and benchmark suites -> `QUALITY-GATES.md`
- `REQ-DATA-001` -> `podium7.evidence`, `podium7.persistence` -> persistence and provenance tests -> `QUALITY-GATES.md`
- `REQ-OPS-001` -> `docs/OPERATOR-INSTALLATION-V1.md`, `scripts/check_package_installation.py`, `scripts/run_operational_readiness.py` -> install/readiness checks -> `QUALITY-GATES.md`

## Gaps

- `TRACEABILITY_GAP`: resolved by the lightweight requirement trace table in this document and the linked quality-gate mapping.
- `VERIFICATION_GAP`: hosted certification remains externally pending, so local verification is the only current acceptance evidence for the baseline.

## Status semantics

- `accepted`: part of the current baseline;
- `supported`: in force but not necessarily a hard baseline gate;
- `pending_external`: held open by a dependency outside the repository;
- `future_candidate`: approved direction but not current baseline.

## Source rule

Do not invent requirements. If a requirement cannot be traced to code, tests, a stable contract, or an approved decision record, keep it out of the baseline.
