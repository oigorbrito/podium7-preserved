# Production Corpus Run V3 execution plan

Status: active

Parent mission: #139
Issue: #140

## Outcome and acceptance criteria

Expand the reproducible source-backed operational replay beyond the 60-record V2 corpus using only already-versioned source-backed gold sets that satisfy the existing `podium7.catalog-identity-golden.v1` contract.

Acceptance:

- add the existing `catalog_identity_year_semantics_challenge_v1.json` source-backed gold set to the operational replay;
- process 72 records end-to-end through batch ingestion, identity resolution, evidence persistence and consumer reads;
- retain HTTPS source locators and deterministic benchmark provenance for every replay record;
- preserve manufacture-year/model-year separation and all existing resolver/evidence/fusion semantics;
- record failures/reviews as outputs rather than changing policy to improve the result;
- do not introduce a new source family, region, semantic field or infrastructure component.

## Boundaries / non-goals

- This is not a production-completeness claim.
- No new external-source research or live acquisition is part of this block.
- No resolver threshold or expected benchmark label changes.
- #141 owns precision/recall and review-load measurement after this corpus is established.
- GitHub Actions issue #112 remains an external validation blocker; do not add runner workarounds.

## Source of truth

- `docs/TECH-DEBT.md`
- `docs/PRODUCTION-CORPUS-RUN-V2.md`
- `docs/CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md`
- `benchmarks/catalog_identity_golden_v1.json`
- `benchmarks/catalog_identity_golden_br_v1.json`
- `benchmarks/catalog_identity_br_adjacent_incomplete_v1.json`
- `benchmarks/catalog_identity_year_semantics_challenge_v1.json`
- `podium7/catalog_operational.py`

## Implementation steps

1. Add a V3 operational corpus test that composes the four already-qualified gold sets.
2. Require 72 source-backed records, source locators and end-to-end consumer readability.
3. Add a V3 design record describing corpus composition and nonclaims.
4. Update current work/index only for this mission.
5. Run repository-required validation when executable runners are available; record #112 if jobs again fail before steps.

## Decisions

- The year-semantics challenge is admitted because it already uses the exact supported golden schema, contains explicit source IDs/HTTPS primary locators, and encodes an owner-selected product invariant. No new semantic inference is required.
- Corpus growth is by composition of retained source-backed evidence, not duplicated/generated synthetic cases.

## Validation evidence / blockers

Pending executable validation. #112 remains the known hosted-runner blocker.
