# Production Corpus Run V3

Status: PENDING — exact source attribution gap identified before executable acceptance

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

The intended composition contains six additional curated identity pairs, therefore twelve additional replay observations, for an intended 72-record operating corpus.

## Provenance blocker discovered during validation

The retained benchmark schema stores `sourceIds` at the **case** level. Several cases defensibly cite more than one primary source, but the schema does not establish which source produced each left/right record or which source supports each individual field.

The previous operational replay selected `sourceIds[0]` and assigned that source to both sides. That behavior was removed because it silently invented source-specific provenance. A case with multiple `sourceIds` now fails closed with `ambiguous case-level source attribution`.

This is intentionally stricter than the previous 72-record replay claim:

```text
CASE_LEVEL_SOURCE_SET != RECORD_SIDE_SOURCE
RECORD_SIDE_SOURCE != FIELD_SOURCE
NO_DEFENSIBLE_MAPPING -> FAIL_CLOSED
```

Single-source benchmark cases remain executable through the existing pipeline and retain exact source/evidence locators and benchmark raw-content references.

## Decision-relevant coverage retained in V3 inputs

The year-semantics challenge still contributes useful curated cases for:

- manufacture-year contradiction while model year agrees;
- missing manufacture-year evidence;
- adjacent explicit model years;
- missing model-year evidence that must remain `REVIEW`;
- overlapping manufacture-year ranges;
- explicit model-year contradiction with equal manufacture year.

These inputs remain valid identity benchmark evidence. They are not yet all admissible as record-level operational replay evidence until source attribution is explicit enough to preserve provenance without inference.

## Acceptance gate

The original 72-record acceptance remains the target, but is currently blocked. It may pass only when every replayed left/right record has defensible source attribution without selecting a source by list order.

Required acceptance remains:

- 72 records from the four versioned datasets **only after exact record-side/source provenance is representable**;
- every record keeps an HTTPS source/evidence locator and benchmark raw-content reference;
- all records execute through batch ingestion with zero record-level ingestion failures;
- `CREATED`, `MATCHED` and `REVIEW` remain exercised;
- resulting canonical records remain readable through the consumer API;
- no resolver, evidence, fusion, ambiguity or publication rule changes are introduced.

## Current executable assertions

`tests/test_production_corpus_run_v3.py` now proves two things deterministically:

1. the current V3 inputs fail closed when a case has ambiguous case-level source attribution;
2. an exactly attributed single-source fixture still traverses the operational replay end to end.

## Nonclaims

- No 72-record operational PASS is claimed while attribution remains ambiguous.
- Case-level source participation is not promoted to record-side or field-level provenance.
- The bounded identity benchmark remains useful even when a case cannot yet be replayed as a single-source operational record.
- No resolver/evidence/fusion threshold is weakened to recover the previous record count.
- No source is selected by convenience or list position.

## Validation state

Static validation identified and corrected the provenance overclaim. Repository-required executable validation remains additionally blocked by #112, where hosted jobs terminate without executing steps. The current block is therefore `PENDING`, not `PASS`.
