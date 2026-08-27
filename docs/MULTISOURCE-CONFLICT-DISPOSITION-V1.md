# Multi-source Conflict Disposition V1

Status: implementation prepared; executable validation pending

Issue: #146
Parent: #127
Related measurement requirement: #141

## Purpose

Make the existing multi-source validation report expose not only that a conflict occurred, but also the explicit `ConflictState` carried by the domain object. This closes the documented requirement to measure conflict count and dispositions without reinterpreting identity `NO_MATCH` or evidence absence as a fusion conflict.

## Existing policy preserved

`DATA-FUSION-AND-CONFLICTS-V1.md` remains unchanged:

- one candidate may canonicalize with provenance;
- unanimous normalized agreement may canonicalize;
- disagreement creates an explicit conflict;
- no silent winner is selected.

`fuse_candidates` creates disagreement conflicts with the domain default `ConflictState.UNRESOLVED`. This block does not add an automatic path to `RESOLVED` or `REVIEW`.

## Report contract

Each multi-source result now carries:

- `disposition`: `CANONICAL`, `CONFLICT`, or `REVIEW`;
- `conflictState`: the underlying conflict state for `CONFLICT`, otherwise null.

The summary additionally carries `conflictsByState`, a deterministic count keyed by the domain state value.

This deliberately keeps two concepts separate:

- `REVIEW` disposition because evidence is absent/insufficient;
- `ConflictState.REVIEW`, which would mean an actual persisted conflict was explicitly moved into review by an audited conflict workflow.

The bounded current corpus contains one normalized-value disagreement, therefore its expected state is `UNRESOLVED`. No other conflict state is manufactured for metric completeness.

## Utility disposition

`MULTISOURCE_CONFLICT_DISPOSITION_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

This is an observability gap, not a new fusion-policy feature. The domain `Conflict` already carries `resolution_state`; the existing bounded multi-source report only exposed `CONFLICT` as a coarse disposition and therefore could not answer the documented requirement to report conflict disposition/state.

The incremental value is:

- expose the already-existing domain state without inventing a second state model;
- make unresolved versus later audited review/resolution distinguishable in measurement;
- preserve evidence-gap `REVIEW` as a separate concept; and
- make `conflictsByState` directly auditable in production-quality reporting.

If synchronization shows an equivalent state projection already exists upstream, this block should be classified `REDUNDANT`; otherwise the current evidence supports integration after executable validation.

## Safety / nonclaims

- No fusion decision rule changes.
- No resolver or publication-policy changes.
- A `NO_MATCH` identity decision is not counted as a data-fusion conflict.
- Missing evidence is not counted as a conflict.
- `RESOLVED` must not appear unless a real audited resolution path produced it.
- Corpus-local counts are not production-wide conflict rates.

## Validation

Focused tests require the disagreement case to remain explicit and `UNRESOLVED`, require non-conflict results to expose no conflict state, and keep evidence-gap reviews separate. Repository-required executable validation remains pending while #112 prevents hosted jobs from executing steps.
