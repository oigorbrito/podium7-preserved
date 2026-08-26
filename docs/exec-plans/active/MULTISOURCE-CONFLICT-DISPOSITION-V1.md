# Multi-source Conflict Disposition V1 execution plan

Status: active

Issue: #146
Parent: #127
Related: #141

## Outcome

Expose explicit domain conflict state in the existing multi-source validation report and measure conflicts by state without changing fusion behavior.

## Acceptance

- `CONFLICT` results expose the underlying `ConflictState`;
- non-conflict results expose no conflict state;
- summary reports deterministic `conflictsByState`;
- the existing disagreement fixture remains `UNRESOLVED`;
- evidence-gap `REVIEW` remains distinct from conflict-review state;
- no silent conflict resolution, resolver change, evidence-policy change, or publication change.

## Implementation

1. Extend `evaluate_multisource_cases` with `conflictState` and state counts.
2. Extend focused tests over the existing bounded corpus.
3. Document the distinction between review disposition and conflict state.
4. Run repository-required validation when hosted runners execute; keep #112 as the external blocker otherwise.
