# Brazil adjacent-year and incomplete-source benchmark

Status: active

## Outcome

Expand the source-backed Brazilian catalog-identity evidence with a focused hard-case slice covering adjacent model-year transitions and cross-source observations that are incomplete in model year or transmission evidence.

## Acceptance criteria

- add a separate benchmark dataset under `benchmarks/` without rewriting the existing golden slices;
- expected `MATCH` / `NO_MATCH` / `REVIEW` labels are curated from source evidence and product policy, never generated from resolver output;
- use primary/official manufacturer sources for the new cases;
- include controls plus adjacent-model-year contradictions and incomplete-source review cases across more than one Brazilian-market manufacturer;
- add focused dataset-integrity and regression tests;
- do not change resolver behavior unless the new evidence demonstrates an in-scope defect;
- update `CATALOG-IDENTITY-BENCHMARK-V1.md` with scope, composition, evidence and measured result;
- repository CI green before integration.

## Boundaries

- no historical candidate retest;
- no public-release/license work;
- no new API, transport or infrastructure;
- no production-quality precision/recall claim from this focused slice;
- preserve `docs/INVARIANTS.md` and the selected Senatran year policy.

## Sources of truth

- [`../../DEVELOPMENT-WORKFLOW.md`](../../DEVELOPMENT-WORKFLOW.md)
- [`../../INVARIANTS.md`](../../INVARIANTS.md)
- [`../../CATALOG-IDENTITY-V2.md`](../../CATALOG-IDENTITY-V2.md)
- [`../../CATALOG-IDENTITY-BENCHMARK-V1.md`](../../CATALOG-IDENTITY-BENCHMARK-V1.md)
- [`../../CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md`](../../CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md)

## Execution

1. Curate a small hard-case dataset from official Toyota, Chevrolet and Volkswagen sources.
2. Add focused integrity/regression tests and evaluate the current resolver without changing it first.
3. If a case exposes a policy defect, make only the smallest evidence-backed resolver correction; otherwise leave resolver code unchanged.
4. Update benchmark documentation with the measured result and remaining limitations.
5. Run required validation, self-review, PR CI and integrate only when green.

## Decisions

- `DOCUMENTED`: expand benchmark coverage by evidence, including adjacent model-year transitions and cross-source incomplete year/transmission evidence.
- `ENGINEERING_CHOICE`: use a separate hard-case slice so the existing golden and year-semantics baselines remain independently reproducible.
- `ENGINEERING_CHOICE`: start with Toyota, Chevrolet and Volkswagen because primary official material provides explicit adjacent-year/configuration evidence and incomplete cross-source representations for the exact documented gaps.

## Validation evidence

Pending.

## Remaining blockers

None known.
