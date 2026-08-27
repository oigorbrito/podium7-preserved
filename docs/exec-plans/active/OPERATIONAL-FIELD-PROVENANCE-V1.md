# Operational Field Provenance V1

Status: implementation prepared; multi-source reconstruction pending
Issue: #166
Parent: #139
Depends on: #145
Blocks: #140 / #141 full operational replay

## Outcome

Prevent benchmark case-level source lists from being promoted into record-level provenance by position. Operational replay may construct a single-source batch record only when either:

1. the benchmark case declares exactly one valid source, leaving no source-selection ambiguity; or
2. explicit `fieldSourceIds` prove exactly one source is common to every present field on that side.

## Retained V3 structural eligibility

Direct inspection of the four retained V3 benchmark files establishes 36 curated cases / 72 record sides.

Before any historical field-provenance reconstruction:

- 6 cases in the global seed benchmark declare exactly one source;
- those 6 cases contribute 12 provenance-eligible record sides through `SOLE_CASE_SOURCE`;
- the remaining 30 cases contribute 60 record sides and are multi-source without populated historical `fieldSourceIds`;
- current structural eligibility is therefore 12 / 72 = 16.67%;
- this is a fixture-derived eligibility boundary, not an executed operational quality result and not a production-completeness claim.

A regression freezes these expected corpus counts. Executable confirmation remains required before integration.

## Acceptance

- no `sourceIds[0]` fallback;
- sole-source cases may replay because no source-selection decision exists;
- every replayed multi-source record has explicit field-level attribution;
- missing attribution fails closed;
- no common source across all fields fails closed;
- multiple fully covering sources remain ambiguous rather than selecting one;
- eligibility can be measured without replaying or silently dropping blocked records;
- source/evidence/resolver/fusion/publication policy is unchanged.

## Boundary

`CatalogBatchEnvelope` binds exactly one `Source` and one `RawEvidence` to a vehicle observation. This block does not create a composite source or multi-source envelope. A side assembled from multiple sources remains non-replayable through this path until explicit attribution identifies one source covering the full side, or a separately justified evidence model is approved.

## Validation

Focused deterministic tests cover positional-source independence, sole-source eligibility, missing field provenance, incompatible field-source coverage, multiple fully covering sources, and the retained V3 12/72 eligibility expectation. The full #140/#141 replay remains PENDING for the other 60 record sides. GitHub-hosted executable validation is independently blocked by #112.
