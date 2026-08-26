# Production Corpus Run V3

Status: implementation prepared; executable validation pending

Issue: #140
Parent mission: #139

## Purpose

Increase the reproducible source-backed operating corpus beyond the 60-record V2 replay using only retained, versioned, already-source-backed gold data. This is product-operation work, not a new source-discovery exercise.

## Corpus composition

V3 reuses the three V2 datasets:

- `catalog_identity_golden_v1.json`;
- `catalog_identity_golden_br_v1.json`;
- `catalog_identity_br_adjacent_incomplete_v1.json`;

and adds the existing source-backed year-semantics regression set:

- `catalog_identity_year_semantics_challenge_v1.json` (`datasetVersion=year-semantics-1.1`).

The added set contains six curated identity pairs, therefore twelve additional replay observations. The operational corpus increases from 60 to 72 records without generating duplicate/synthetic filler cases.

## Why this dataset is admissible

The existing `build_source_backed_operational_records` contract accepts only `podium7.catalog-identity-golden.v1` datasets with a non-empty `datasetVersion`, explicit source IDs and source locators. The year-semantics challenge satisfies that exact contract and is already part of the repository's selected Senatran-aligned identity policy regression evidence.

It contributes decision-relevant cases for:

- manufacture-year contradiction while model year agrees;
- missing manufacture-year evidence;
- adjacent explicit model years;
- missing model-year evidence that must remain `REVIEW`;
- overlapping manufacture-year ranges;
- explicit model-year contradiction with equal manufacture year.

## Acceptance gate

- 72 records are produced from the four versioned datasets;
- every record keeps an HTTPS source/evidence locator and benchmark raw-content reference;
- all 72 execute through batch ingestion with zero record-level ingestion failures;
- `CREATED`, `MATCHED` and `REVIEW` remain exercised;
- resulting canonical records remain readable through the consumer API;
- no resolver, evidence, fusion, ambiguity or publication rule changes are introduced.

## Nonclaims

- 72 records are still a bounded operating corpus, not production or market completeness.
- Adding the year-semantics challenge does not increase geographic breadth by itself; it increases decision-semantic coverage within already-documented evidence.
- This block does not claim improved precision/recall or reduced review load. #141 owns those measurements after executable V3 evidence exists.
- No new source family, new infrastructure or new semantic-field policy is selected by V3.

## Validation state

The implementation is deterministic and committed as `tests/test_production_corpus_run_v3.py`. Repository-required executable validation remains pending while #112 prevents GitHub-hosted jobs from executing steps. Do not mark this corpus PASS until the focused test and required repository validation execute successfully.
