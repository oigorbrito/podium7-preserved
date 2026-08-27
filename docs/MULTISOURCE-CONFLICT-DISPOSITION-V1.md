# Multi-source Conflict Disposition V1

Status: implementation prepared; integration pending repository validation.

Issue: #146
PR: #147
Parent: #127 / PR #131

## Purpose

Expose the existing domain `ConflictState` in the bounded multi-source validation report so operational measurements can distinguish an actual persisted fusion conflict from a generic evidence-gap `REVIEW` disposition.

## Incremental contract

Each validation result adds `conflictState` when `disposition == "CONFLICT"`, otherwise `null`. The summary adds deterministic `conflictsByState` counts.

The current fusion model creates normalized-value disagreements as `ConflictState.UNRESOLVED`. This block does not add automatic resolution behavior.

## Corrected provenance denominator preserved

The branch is rebuilt on the synchronized corrected #131 head. Candidate-bearing canonical/conflict cases are the only provenance-applicable cases. Evidence-gap REVIEW cases remain `provenanceComplete = null` and outside the denominator.

Bounded fixture expectations: 3 canonical, 1 corroborated, 1 conflict (`UNRESOLVED`), 2 evidence-gap REVIEW, 4 provenance-applicable / 4 complete, 0 incorrect dispositions and 0 resolver-policy changes.

These are fixture expectations, not executable PASS claims or production-wide rates.

## Utility decision

`MULTISOURCE_CONFLICT_DISPOSITION_UTILITY = INTEGRATE_AFTER_VALIDATION`.

This closes an observability gap: the domain already stores conflict resolution state while the report previously exposed only the coarse `CONFLICT` disposition.

## Safety

No fusion decision, resolver, evidence, source or publication rule changes. REVIEW disposition is not the same as `ConflictState.REVIEW`, and measurement never changes conflict state.

## Validation

Focused regressions cover `UNRESOLVED`, state counts, null state on non-conflicts, REVIEW separation and the corrected #131 provenance denominator. Repository validation remains blocked by #112.
