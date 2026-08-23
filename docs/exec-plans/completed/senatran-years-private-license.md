# Senatran year semantics and private licensing

Status: completed

Integrated: 2026-08-23 via PR #42.

## Outcome

Implemented the owner-selected vehicle-year policy and recorded Podium 7 as private/proprietary without changing unrelated catalog behavior.

## Decisions

- `manufacture_year_*` and `model_year_*` remain separate fields, consistent with Senatran/RENAVAM semantics.
- Explicit non-overlap in either year dimension is a deterministic `NO_MATCH`.
- Model-year evidence present on only one side of an otherwise auto-matchable pair routes to `REVIEW` instead of automatic `MATCH`, unless stronger identity evidence establishes the match.
- Missing manufacture-year evidence alone does not block a match when model-year and the other required identity evidence agree.
- Podium 7 remains private/proprietary. No public software license is granted; MIT/Apache/open-source selection is deferred until the product is operational.

## Validation

- source-backed year-semantics regression is exact at 6/6;
- existing catalog golden slices remained green;
- release readiness intentionally blocks public/package release under `PRIVATE_PROPRIETARY`;
- packaging metadata claims no public license;
- repository visibility is private;
- CI run 32632946556 passed 305/305 isolated tests before integration.

No historical candidate-test battery was rerun.
