# Podium 7 Quality Gates

Status: current quality-gate authority

## Gate model

Quality gates are pass/fail checks for the current private baseline. They are not aspirational checklists.

## Functional suitability

- core catalog, acquisition, review, and export flows must remain available through documented commands or validated tests;
- conservative identity resolution must remain intact;
- review outcomes must be durable and inspectable.

## Reliability

- runtime health and repository readiness checks must pass;
- focused regression and sequential tests must pass for the exact candidate under validation;
- operational artifacts must be reproducible from the repository state.

## Operability

- installation and first-run instructions must work on a supported local environment;
- operator workflows must have documented commands and failure modes;
- troubleshooting and recovery paths must be documented.

## Maintainability

- canonical documents must be singular and linked from the index;
- stale trackers must not compete with current-state authority;
- durable decisions must live in design records or ADRs, not in chat.

## Security and provenance

- repository secrets must not be introduced into documentation;
- evidence and provenance must remain attached to persisted outcomes;
- public release remains blocked while the software is private/proprietary.

## Installation and persistence

- clean install must be validated;
- SQLite-backed persistence behavior must remain documented and testable;
- backup and restore boundaries must be explicit.

## Recovery

- health and readiness must provide actionable failure signals;
- operational docs must describe the minimum recovery path for a private operator;
- generated artifacts must be segregated from source authority.

## Testing

- harness checks must pass;
- focused behavior tests must pass;
- sequential validation must be available for integration;
- repository CI remains the hosted certification gate when external execution is available.

## Requirement linkage

- functional suitability gates cover `REQ-FUNC-*`;
- data and provenance gates cover `REQ-DATA-*`;
- install, operations, and recovery gates cover `REQ-OPS-*`;
- quality and verification gates cover `REQ-QUAL-*`.

## Gate relation

The current documented gates are defined in `docs/CLOSEOUT-PLAN.md`. Those gates are the enforcement layer for this quality model.
