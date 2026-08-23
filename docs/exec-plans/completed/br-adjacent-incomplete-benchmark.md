# Brazil adjacent-year and incomplete-source benchmark

Status: completed

## Outcome

Expanded the source-backed Brazilian catalog-identity evidence with a focused hard-case slice covering adjacent model-year transitions and cross-source observations that are incomplete in model year or transmission evidence.

## Acceptance criteria

- added a separate benchmark dataset under `benchmarks/` without rewriting existing golden slices;
- expected `MATCH` / `NO_MATCH` / `REVIEW` labels were curated from source evidence and product policy, never generated from resolver output;
- used primary/official Toyota do Brasil, Chevrolet Brasil and Volkswagen do Brasil sources;
- included a positive control, adjacent-model-year contradictions and incomplete-source review cases across three Brazilian-market manufacturers;
- added focused dataset-integrity and regression tests;
- resolver behavior did not change because the new evidence matched the selected policy;
- updated `CATALOG-IDENTITY-BENCHMARK-V1.md` with scope, composition, evidence and result;
- repository CI was green before integration.

## Boundaries

- no historical candidate retest;
- no public-release/license work;
- no new API, transport or infrastructure;
- no production-quality precision/recall claim from this focused slice;
- preserved `docs/INVARIANTS.md` and the selected Senatran year policy.

## Sources of truth

- [`../../DEVELOPMENT-WORKFLOW.md`](../../DEVELOPMENT-WORKFLOW.md)
- [`../../INVARIANTS.md`](../../INVARIANTS.md)
- [`../../CATALOG-IDENTITY-V2.md`](../../CATALOG-IDENTITY-V2.md)
- [`../../CATALOG-IDENTITY-BENCHMARK-V1.md`](../../CATALOG-IDENTITY-BENCHMARK-V1.md)
- [`../../CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md`](../../CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md)

## Decisions

- `DOCUMENTED`: expand benchmark coverage by evidence, including adjacent model-year transitions and cross-source incomplete year/transmission evidence.
- `ENGINEERING_CHOICE`: use a separate hard-case slice so existing golden and year-semantics baselines remain independently reproducible.
- `ENGINEERING_CHOICE`: start with Toyota, Chevrolet and Volkswagen because primary official material provided evidence for the documented gaps.

## Validation evidence

- Dataset: `benchmarks/catalog_identity_br_adjacent_incomplete_v1.json`, version `br-adjacent-incomplete-1.0`.
- Composition: 6 cases — 1 `MATCH`, 2 `NO_MATCH`, 3 `REVIEW`; 11 first-party source records.
- PR: #44 `Expand Brazil identity benchmark with adjacent-year hard cases`.
- Merge candidate head: `eaa13b655da64a3a6ae72ab54a53be4a11e2ea7c`.
- GitHub Actions run: `32642577486`, job `97201836107`.
- `HARNESS PASS`.
- Runtime health: `PASS`, schema version 1.
- Focused new tests #96 and #97: PASS.
- Repository suite: `307/307` tests executed one by one, PASS.
- Validation artifact: `podium7-validation-evidence`, artifact ID `9494004040`, SHA-256 `75a2d812c541ad0a2645de28abad9aa3741fa462ba232de709964fbe7349330f`.
- Resolver change required: **NO**; all six independently curated labels matched current selected policy.
- PR #44 squash-merged to main as `5b29a52b0c2d6a711781b083cb77d0a877b6c9b5`.

## Remaining blockers

None in scope. Broader benchmark expansion remains governed by the documented evidence-driven expansion plan rather than this completed work unit.
