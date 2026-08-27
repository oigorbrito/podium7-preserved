# Multi-source Conflict Disposition V1

Status: implementation prepared; integration pending repository validation.

Issue: #146
PR: #147
Parent: #127 / PR #131

## Purpose

Expose the existing domain `ConflictState` in the bounded multi-source validation report so operational measurements can distinguish an actual persisted fusion conflict from a generic evidence-gap `REVIEW` disposition.

## Incremental contract

Each validation result adds:

- `conflictState`: the underlying conflict state when `disposition == "CONFLICT"`, otherwise `null`.

The summary adds:

- `conflictsByState`: deterministic counts keyed by `ConflictState.value`.

The current fusion model creates normalized-value disagreements as `ConflictState.UNRESOLVED`. This block does not add an automatic path to `RESOLVED` or `REVIEW`.

## Corrected provenance denominator preserved

This branch is rebuilt on the corrected #131 head. Candidate-bearing canonical/conflict cases remain provenance-applicable only when the fusion references exactly the expected candidate set and canonical provenance derives from every candidate. Evidence-gap REVIEW cases with no candidates remain `provenanceComplete = null` and are excluded from the provenance denominator.

For the bounded six-case corpus the encoded expectations remain:

- 3 canonical;
- 1 corroborated;
- 1 conflict, state `UNRESOLVED`;
- 2 evidence-gap REVIEW;
- 4 provenance-applicable cases, 4 complete;
- 0 incorrect dispositions;
- 0 resolver-policy changes.

These are fixture expectations, not executable PASS claims or production-wide rates.

## Safety / nonclaims

- No fusion decision rule changes.
- No conflict is manufactured for missing evidence.
- A REVIEW disposition is not the same thing as `ConflictState.REVIEW`.
- No resolution state is changed by measurement.
- No resolver, evidence, source or publication policy changes.

## Utility decision

`MULTISOURCE_CONFLICT_DISPOSITION_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

The capability closes an observability gap: the domain already stores conflict resolution state, while the validation report previously exposed only `CONFLICT`. Reporting that existing state is useful for auditability without duplicating or redefining fusion semantics.

## Validation

Focused regressions cover the explicit `UNRESOLVED` disagreement state, `conflictsByState`, null conflict state for canonical/REVIEW outcomes, separation of evidence-gap REVIEW from conflict-state REVIEW, and retention of the corrected #131 provenance denominator and malformed-fixture protections.

Repository harness, sequential suite and PR merge-candidate CI remain required. #112 remains the external hosted-runner blocker.
