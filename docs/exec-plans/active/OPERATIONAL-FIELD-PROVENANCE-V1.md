# Operational Field Provenance V1

Status: implementation prepared; retained-corpus eligibility execution pending
Issue: #166
Parent: #139
Depends on: #145
Blocks: #140 / #141 full operational replay

## Outcome

Prevent benchmark case-level source lists from being promoted into record-level provenance by position while allowing records whose source is genuinely unambiguous.

## Replay contract

A side is replayable through the existing single-source `CatalogBatchEnvelope` only when:

1. the case declares exactly one valid `sourceId`; or
2. explicit `fieldSourceIds` identify exactly one source common to every present field on that side.

Multi-source cases without complete attribution remain blocked. No source is selected from list order, source description, rationale or convenience.

## Eligibility measurement

`measure_operational_provenance_eligibility()` validates the benchmark and classifies every case side without ingesting blocked observations. It reports replayable/blocked counts, replayable method (`SOLE_CASE_SOURCE` or `EXPLICIT_FIELD_ATTRIBUTION`) and explicit blocked reasons.

This allows the project to quantify the defensible subset before attempting operational replay, without claiming blocked records as failures or silently excluding them from a supposed full-corpus run.

## Acceptance

- no positional `sourceIds[0]` fallback;
- sole-source cases are not artificially blocked;
- multi-source replay requires complete explicit attribution;
- missing attribution fails closed;
- no common source across all fields fails closed;
- multiple fully covering sources remain ambiguous rather than selecting one;
- malformed benchmark/provenance containers fail closed through #145's parser;
- source/evidence/resolver/fusion/publication policy is unchanged.

## Boundary

`CatalogBatchEnvelope` binds exactly one `Source` and one `RawEvidence` to a vehicle observation. This block does not create a composite source or multi-source envelope. A genuinely multi-source side therefore remains non-replayable through this path until explicit attribution proves a unique full-record source or a separately justified evidence model exists.

## Validation

Focused deterministic tests cover positional-source independence, sole-source replay, missing/duplicate field provenance, incompatible field-source coverage, multiple fully covering sources, and mixed eligibility reporting without replaying blocked records.

The retained V3 corpus still has no historical `fieldSourceIds`; the exact numerical replayable subset remains an executable measurement, not a static claim. Full #140/#141 replay remains PENDING for unresolved multi-source records. GitHub-hosted executable validation is independently blocked by #112.
