# Senatran year semantics and private licensing

Status: active

## Outcome

Implement the owner-selected product rules for vehicle years and software distribution status without changing unrelated catalog behavior.

## Decisions

- Keep `manufacture_year_*` and `model_year_*` as separate fields, consistent with Senatran/RENAVAM semantics.
- Explicit non-overlap in either year dimension remains a deterministic `NO_MATCH`.
- If model-year evidence exists on only one side of an otherwise auto-matchable pair, route to `REVIEW` instead of automatic `MATCH`.
- Missing manufacture-year evidence alone does not block a match when model-year and the other required identity evidence agree.
- Podium 7 remains private/proprietary for now. No public redistribution/use license is granted; MIT/Apache/open-source selection is deferred until the product is operational.

## Acceptance

- year-semantics challenge becomes an exact regression gate;
- existing golden catalog identity slices do not regress;
- release readiness reports private/proprietary status as an intentional release blocker rather than `UNKNOWN`;
- package metadata does not claim a public license;
- repository remains private;
- normal CI passes before integration.
